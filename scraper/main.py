import argparse
from pathlib import Path
import yaml
from sqlalchemy import select

from scraper.parser import (
    parse_boxscore,
    parse_game_metadata,
    parse_players,
    parse_plays_and_pitches,
)
from scraper.sources.mlb_stats_api import MLBStatsClient
from storage.db import (
    BattingGameStat,
    FieldingGameStat,
    Game,
    Pitch,
    PitchingGameStat,
    PlateAppearance,
    Player,
    Team,
    init_db,
)

BASE_DIR = Path(__file__).resolve().parent.parent


def load_config() -> dict:
    with open(BASE_DIR / "config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def upsert_teams(session, teams: list[dict], known_teams: set[int]) -> None:
    for t in teams:
        session.merge(Team(**t))
        known_teams.add(t["team_id"])
    session.commit()


def ensure_schedule_teams(session, schedule: list[dict], known_teams: set[int]) -> None:
    """Garantiza que cualquier equipo presente en el calendario exista en la tabla teams."""
    added = False
    for g in schedule:
        for key in ("home_team_id", "away_team_id"):
            tid = g[key]
            if tid not in known_teams:
                session.merge(Team(team_id=tid, name=f"Team {tid}"))
                known_teams.add(tid)
                added = True
    if added:
        session.commit()


def ensure_players(session, known_ids: set[int], players: list[dict]) -> None:
    for p in players:
        pid = p["player_id"]
        if pid not in known_ids:
            session.merge(Player(**p))
            known_ids.add(pid)


def run_pipeline(seasons: list[int] | None = None) -> None:
    config = load_config()
    db_path = BASE_DIR / config["storage"]["sqlite_path"]
    db_path.parent.mkdir(parents=True, exist_ok=True)

    _, Session = init_db(str(db_path))
    client = MLBStatsClient(config)
    target_seasons = seasons or config["scraping"]["seasons_pilot"]

    with Session() as session:
        known_teams = set(session.scalars(select(Team.team_id)).all())
        known_players = set(session.scalars(select(Player.player_id)).all())

        for season in target_seasons:
            print(f"\n=== Temporada {season} ===")
            upsert_teams(session, client.fetch_teams(season), known_teams)
            schedule = client.fetch_schedule(season)
            ensure_schedule_teams(session, schedule, known_teams)
            print(f"Juegos oficiales encontrados (sin pretemporada): {len(schedule)}")

            done_pks = set(
                session.scalars(
                    select(Game.game_pk).where(
                        Game.season == season, Game.is_completed.is_(True)
                    )
                ).all()
            )

            for idx, g in enumerate(schedule, start=1):
                pk = g["game_pk"]
                if pk in done_pks:
                    continue

                try:
                    game_row = Game(**g)
                    session.merge(game_row)

                    if not g["is_completed"]:
                        session.commit()
                        continue

                    feed = client.fetch_game_feed(pk)
                    meta = parse_game_metadata(feed)
                    for k, v in meta.items():
                        setattr(game_row, k, v)
                    session.merge(game_row)

                    players = parse_players(feed.get("gameData", {}))
                    ensure_players(session, known_players, players)

                    live = feed.get("liveData", {})
                    box = parse_boxscore(pk, live)

                    # Asegura que todo jugador en boxscore exista en players
                    for rows in box.values():
                        for r in rows:
                            if r["player_id"] not in known_players:
                                ensure_players(
                                    session,
                                    known_players,
                                    [{"player_id": r["player_id"], "full_name": f"Player {r['player_id']}"}],
                                )

                    session.add_all([BattingGameStat(**r) for r in box["batting"]])
                    session.add_all([PitchingGameStat(**r) for r in box["pitching"]])
                    session.add_all([FieldingGameStat(**r) for r in box["fielding"]])

                    plays = parse_plays_and_pitches(
                        pk, g["home_team_id"], g["away_team_id"], live
                    )
                    for item in plays:
                        pa_data = item["pa"]
                        for pid_key in ("batter_id", "pitcher_id"):
                            pid = pa_data[pid_key]
                            if pid not in known_players:
                                ensure_players(
                                    session,
                                    known_players,
                                    [{"player_id": pid, "full_name": f"Player {pid}"}],
                                )

                        pa_obj = PlateAppearance(**pa_data)
                        session.add(pa_obj)
                        session.flush()
                        if item["pitches"]:
                            session.add_all(
                                [Pitch(pa_id=pa_obj.id, **pt) for pt in item["pitches"]]
                            )

                    session.commit()
                    done_pks.add(pk)
                    if idx % 25 == 0 or idx == len(schedule):
                        print(f"  Progreso {season}: {idx}/{len(schedule)} procesados")

                except Exception as err:
                    session.rollback()
                    print(f"  [ERROR] gamePk={pk}: {err}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scraper LMP -> SQLite")
    parser.add_argument("--all", action="store_true", help="Ejecuta todo el rango configurado (2006-2026)")
    parser.add_argument("--start", type=int, help="Temporada inicial")
    parser.add_argument("--end", type=int, help="Temporada final")
    args = parser.parse_args()

    cfg = load_config()
    if args.all:
        s0, s1 = cfg["scraping"]["seasons_all_range"]
        run_pipeline(list(range(s1, s0 - 1, -1)))  # De más reciente (2026) a más antigua (2006)
    elif args.start and args.end:
        run_pipeline(list(range(args.end, args.start - 1, -1)))
    else:
        run_pipeline()
