from pathlib import Path
import sqlite3
import time
import pandas as pd
import requests
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "yaquis_lmp.db"

MLB_HEADSHOT_TMPL = (
    "https://img.mlbstatic.com/mlb-photos/image/upload/"
    "d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/{pid}/headshot/67/current"
)

SCOUT_COLUMNS = {
    "birth_country": "VARCHAR(60)",
    "birth_city": "VARCHAR(80)",
    "birth_date": "VARCHAR(20)",
    "height": "VARCHAR(20)",
    "weight": "INTEGER",
    "mlb_debut_date": "VARCHAR(20)",
    "headshot_url": "VARCHAR(255)",
}


def get_with_retry(
    session: requests.Session, url: str, params: dict | None = None, max_retries: int = 4
) -> dict:
    for attempt in range(max_retries):
        try:
            resp = session.get(url, params=params, timeout=25)
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
    return {}


def ensure_scout_columns(conn: sqlite3.Connection) -> None:
    existing = {
        row[1] for row in conn.execute("PRAGMA table_info(players)").fetchall()
    }
    for col, sql_type in SCOUT_COLUMNS.items():
        if col not in existing:
            conn.execute(f"ALTER TABLE players ADD COLUMN {col} {sql_type}")
    conn.commit()


def enrich_players_scout(conn: sqlite3.Connection, session: requests.Session) -> None:
    ensure_scout_columns(conn)
    pids = [
        r[0]
        for r in conn.execute(
            "SELECT player_id FROM players WHERE birth_country IS NULL"
        ).fetchall()
    ]
    print(f"Jugadores por enriquecer con perfil scout: {len(pids)}")

    batch_size = 100
    for i in range(0, len(pids), batch_size):
        batch = pids[i : i + batch_size]
        ids_str = ",".join(str(x) for x in batch)
        data = get_with_retry(
            session,
            "https://statsapi.mlb.com/api/v1/people",
            params={"personIds": ids_str},
        )
        people = {p["id"]: p for p in data.get("people", [])}

        updates = []
        for pid in batch:
            p = people.get(pid, {})
            updates.append((
                p.get("birthCountry") or "SIN_DATO",
                p.get("birthCity") or "SIN_DATO",
                p.get("birthDate"),
                p.get("height"),
                p.get("weight"),
                p.get("mlbDebutDate"),
                MLB_HEADSHOT_TMPL.format(pid=pid),
                pid,
            ))
        conn.executemany("""
            UPDATE players
            SET birth_country = ?, birth_city = ?, birth_date = ?,
                height = ?, weight = ?, mlb_debut_date = ?, headshot_url = ?
            WHERE player_id = ?
        """, updates)
        conn.commit()
        time.sleep(0.2)

    print("Perfil scout de jugadores actualizado.")


def fix_is_risp_for_seasons(
    conn: sqlite3.Connection, session: requests.Session, seasons: tuple[int, ...] = (2025, 2026)
) -> None:
    placeholders = ",".join("?" for _ in seasons)
    pks = [
        r[0]
        for r in conn.execute(
            f"SELECT game_pk FROM v_valid_games WHERE season IN ({placeholders}) AND has_pbp = 1 ORDER BY season DESC, game_date",
            seasons,
        ).fetchall()
    ]
    print(f"Recalculando is_risp pre-turno en {len(pks)} juegos (temporadas {seasons})...")

    for idx, pk in enumerate(pks, start=1):
        feed = get_with_retry(
            session,
            f"https://statsapi.mlb.com/api/v1.1/game/{pk}/feed/live",
        )
        plays = feed.get("liveData", {}).get("plays", {}).get("allPlays", [])

        current_half_key = None
        prev_men_on_base = "Empty"
        updates = []

        for play in plays:
            about = play.get("about", {})
            matchup = play.get("matchup", {})
            half_key = (about.get("inning"), about.get("halfInning", "top"))
            if half_key != current_half_key:
                current_half_key = half_key
                prev_men_on_base = "Empty"

            is_risp = 1 if prev_men_on_base in ("RISP", "Loaded") else 0
            prev_men_on_base = matchup.get("splits", {}).get("menOnBase", "Empty")

            at_bat_idx = play.get("atBatIndex")
            if at_bat_idx is not None:
                updates.append((is_risp, pk, at_bat_idx))

        conn.executemany(
            "UPDATE plate_appearances SET is_risp = ? WHERE game_pk = ? AND at_bat_index = ?",
            updates,
        )
        conn.commit()
        if idx % 50 == 0 or idx == len(pks):
            print(f"  Progreso is_risp: {idx}/{len(pks)} juegos")
        time.sleep(0.15)


def revalidate_risp(conn: sqlite3.Connection) -> None:
    print("\n=== REVALIDACIÓN YAQUIS 2025-26: SPLITS RISP CORREGIDOS ===")
    df = pd.read_sql_query("""
        SELECT
            CASE
                WHEN g.game_stage = 'PLAYOFFS' THEN 'Playoffs'
                WHEN g.game_date <= '2025-11-23' THEN '1ra Vuelta'
                ELSE '2da Vuelta'
            END AS etapa,
            pa.is_risp,
            COUNT(*) AS PA,
            SUM(CASE WHEN pa.event_type NOT IN ('walk','intent_walk','hit_by_pitch','sac_fly','sac_bunt','sac_fly_double_play','catcher_interf') THEN 1 ELSE 0 END) AS AB,
            SUM(CASE WHEN pa.event_type IN ('single','double','triple','home_run') THEN 1 ELSE 0 END) AS H,
            SUM(CASE WHEN pa.event_type = 'home_run' THEN 1 ELSE 0 END) AS HR,
            SUM(CASE WHEN pa.event_type IN ('walk','intent_walk') THEN 1 ELSE 0 END) AS BB,
            SUM(CASE WHEN pa.event_type IN ('strikeout','strikeout_double_play') THEN 1 ELSE 0 END) AS SO,
            SUM(pa.rbi) AS RBI
        FROM plate_appearances pa
        JOIN v_valid_games g ON pa.game_pk = g.game_pk
        WHERE g.season = 2025 AND pa.batting_team_id = 680
        GROUP BY etapa, pa.is_risp
        ORDER BY etapa, pa.is_risp
    """, conn)
    df["AVG"] = (df["H"] / df["AB"]).round(3)
    print(df.to_string(index=False))

    print("\n=== MUESTRA SCOUT YAQUIS 2025-26 ===")
    scout_df = pd.read_sql_query("""
        SELECT DISTINCT pl.player_id, pl.full_name, pl.birth_country, pl.height, pl.weight, pl.bat_side, pl.pitch_hand
        FROM batting_game_stats b
        JOIN v_valid_games g ON b.game_pk = g.game_pk
        JOIN players pl ON b.player_id = pl.player_id
        WHERE g.season = 2025 AND b.team_id = 680
        LIMIT 12
    """, conn)
    print(scout_df.to_string(index=False))


def main() -> None:
    with open(BASE_DIR / "config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    session = requests.Session()
    session.headers.update({"User-Agent": cfg["scraping"]["user_agent"]})

    with sqlite3.connect(DB_PATH, timeout=30) as conn:
        enrich_players_scout(conn, session)
        fix_is_risp_for_seasons(conn, session, (2025, 2026))
        revalidate_risp(conn)


if __name__ == "__main__":
    main()
