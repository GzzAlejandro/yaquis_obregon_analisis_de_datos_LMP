import marimo

__generated_with = "0.25.2"
app = marimo.App(width="wide")


@app.cell
def _():
    from pathlib import Path
    import sqlite3
    import marimo as mo
    import pandas as pd

    BASE_DIR = Path(__file__).resolve().parent.parent
    DB_PATH = BASE_DIR / "data" / "yaquis_lmp.db"
    YAQUIS_ID = 680
    VUELTA_1_FIN = "2025-11-23"
    return DB_PATH, VUELTA_1_FIN, YAQUIS_ID, mo, pd, sqlite3


@app.cell
def _(mo):
    mo.md("""
# EDA Inicial — Yaquis de Obregón y Contexto LMP (2006–2026)

Análisis variable por variable (ofensiva, pitcheo abridor/relevista y defensa)
separando la temporada **2025–26** en **1ra Vuelta**, **2da Vuelta** y **Playoffs**.
""")
    return


@app.cell
def _(DB_PATH, VUELTA_1_FIN, YAQUIS_ID, pd, sqlite3):
    with sqlite3.connect(DB_PATH, timeout=30) as _conn:
        # 1. Contexto histórico de Yaquis (2006-2026)
        yaquis_hist_df = pd.read_sql_query(f"""
            WITH yaquis_games AS (
                SELECT
                    season,
                    game_stage,
                    CASE WHEN home_team_id = {YAQUIS_ID} THEN home_score ELSE away_score END AS runs_for,
                    CASE WHEN home_team_id = {YAQUIS_ID} THEN away_score ELSE home_score END AS runs_against
                FROM v_valid_games
                WHERE home_team_id = {YAQUIS_ID} OR away_team_id = {YAQUIS_ID}
            )
            SELECT
                season,
                game_stage,
                COUNT(*) AS juegos,
                SUM(CASE WHEN runs_for > runs_against THEN 1 ELSE 0 END) AS ganados,
                SUM(CASE WHEN runs_for < runs_against THEN 1 ELSE 0 END) AS perdidos,
                ROUND(1.0 * SUM(CASE WHEN runs_for > runs_against THEN 1 ELSE 0 END) / COUNT(*), 3) AS pct_victorias,
                SUM(runs_for) AS carreras_favor,
                SUM(runs_against) AS carreras_contra,
                SUM(runs_for) - SUM(runs_against) AS diferencial
            FROM yaquis_games
            GROUP BY season, game_stage
            ORDER BY season DESC, game_stage
        """, _conn)

        etapa_sql = f"""
            CASE
                WHEN g.game_stage = 'PLAYOFFS' THEN 'Playoffs'
                WHEN g.game_date <= '{VUELTA_1_FIN}' THEN '1ra Vuelta'
                ELSE '2da Vuelta'
            END
        """

        # 2. Récord por equipo y etapa (2025-26)
        standings_2025_df = pd.read_sql_query(f"""
            WITH team_games AS (
                SELECT {etapa_sql} AS etapa, g.home_team_id AS team_id, g.home_team_name AS equipo,
                       g.home_score AS rf, g.away_score AS ra
                FROM v_valid_games g WHERE g.season = 2025
                UNION ALL
                SELECT {etapa_sql} AS etapa, g.away_team_id AS team_id, g.away_team_name AS equipo,
                       g.away_score AS rf, g.home_score AS ra
                FROM v_valid_games g WHERE g.season = 2025
            )
            SELECT
                etapa,
                team_id,
                equipo,
                COUNT(*) AS JJ,
                SUM(CASE WHEN rf > ra THEN 1 ELSE 0 END) AS JG,
                SUM(CASE WHEN rf < ra THEN 1 ELSE 0 END) AS JP,
                ROUND(1.0 * SUM(CASE WHEN rf > ra THEN 1 ELSE 0 END) / COUNT(*), 3) AS PCT,
                SUM(rf) AS CF,
                SUM(ra) AS CC,
                SUM(rf) - SUM(ra) AS DIF
            FROM team_games
            GROUP BY etapa, team_id, equipo
        """, _conn)

        # 3. Bateo por equipo y etapa (2025-26)
        bat_2025_df = pd.read_sql_query(f"""
            SELECT
                {etapa_sql} AS etapa,
                CASE WHEN b.team_id = 674 THEN 'Charros de Jalisco' ELSE t.name END AS equipo,
                b.team_id,
                COUNT(DISTINCT g.game_pk) AS juegos,
                SUM(b.plate_appearances) AS PA,
                SUM(b.at_bats) AS AB,
                SUM(b.runs) AS R,
                SUM(b.hits) AS H,
                SUM(b.doubles) AS "2B",
                SUM(b.triples) AS "3B",
                SUM(b.home_runs) AS HR,
                SUM(b.walks) AS BB,
                SUM(b.hit_by_pitch) AS HBP,
                SUM(b.strikeouts) AS SO,
                SUM(b.stolen_bases) AS SB,
                ROUND(1.0 * SUM(b.hits) / NULLIF(SUM(b.at_bats), 0), 3) AS AVG,
                ROUND(1.0 * (SUM(b.hits) + SUM(b.walks) + SUM(b.hit_by_pitch))
                      / NULLIF(SUM(b.at_bats) + SUM(b.walks) + SUM(b.hit_by_pitch) + SUM(b.sac_flies), 0), 3) AS OBP,
                ROUND(1.0 * SUM(b.total_bases) / NULLIF(SUM(b.at_bats), 0), 3) AS SLG,
                ROUND(1.0 * (SUM(b.hits) - SUM(b.home_runs))
                      / NULLIF(SUM(b.at_bats) - SUM(b.strikeouts) - SUM(b.home_runs) + SUM(b.sac_flies), 0), 3) AS BABIP,
                ROUND(100.0 * SUM(b.walks) / NULLIF(SUM(b.plate_appearances), 0), 1) AS "BB%",
                ROUND(100.0 * SUM(b.strikeouts) / NULLIF(SUM(b.plate_appearances), 0), 1) AS "K%"
            FROM batting_game_stats b
            JOIN v_valid_games g ON b.game_pk = g.game_pk
            JOIN teams t ON b.team_id = t.team_id
            WHERE g.season = 2025
            GROUP BY etapa, b.team_id
        """, _conn)
        bat_2025_df["OPS"] = (bat_2025_df["OBP"] + bat_2025_df["SLG"]).round(3)

        # 4. Pitcheo por equipo, etapa y rol (Abridor vs Relevista, 2025-26)
        pit_2025_df = pd.read_sql_query(f"""
            SELECT
                {etapa_sql} AS etapa,
                CASE WHEN p.team_id = 674 THEN 'Charros de Jalisco' ELSE t.name END AS equipo,
                p.team_id,
                CASE WHEN p.games_started = 1 THEN 'Abridor' ELSE 'Relevista' END AS rol,
                ROUND(SUM(p.outs) / 3.0, 1) AS IP,
                ROUND(9.0 * SUM(p.earned_runs) / NULLIF(SUM(p.outs) / 3.0, 0), 2) AS ERA,
                ROUND(9.0 * SUM(p.runs) / NULLIF(SUM(p.outs) / 3.0, 0), 2) AS RA9,
                ROUND((SUM(p.hits) + SUM(p.walks)) / NULLIF(SUM(p.outs) / 3.0, 0), 2) AS WHIP,
                ROUND(9.0 * SUM(p.strikeouts) / NULLIF(SUM(p.outs) / 3.0, 0), 2) AS K9,
                ROUND(9.0 * SUM(p.walks) / NULLIF(SUM(p.outs) / 3.0, 0), 2) AS BB9,
                ROUND(9.0 * SUM(p.home_runs) / NULLIF(SUM(p.outs) / 3.0, 0), 2) AS HR9,
                ROUND(100.0 * SUM(p.strikes) / NULLIF(SUM(p.pitches_thrown), 0), 1) AS "Strike%",
                SUM(p.inherited_runners) AS IR,
                SUM(p.inherited_runners_scored) AS IRS
            FROM pitching_game_stats p
            JOIN v_valid_games g ON p.game_pk = g.game_pk
            JOIN teams t ON p.team_id = t.team_id
            WHERE g.season = 2025
            GROUP BY etapa, p.team_id, rol
        """, _conn)

        # 5. Defensa + DER (Eficiencia Defensiva sobre Bolas en Juego) por equipo y etapa (2025-26)
        fld_2025_df = pd.read_sql_query(f"""
            WITH bip AS (
                SELECT
                    {etapa_sql} AS etapa,
                    pa.pitching_team_id AS team_id,
                    COUNT(*) AS BIP_total,
                    SUM(CASE WHEN pa.is_out = 1 THEN 1 ELSE 0 END) AS BIP_outs
                FROM plate_appearances pa
                JOIN v_valid_games g ON pa.game_pk = g.game_pk
                WHERE g.season = 2025
                  AND pa.hit_coord_x IS NOT NULL
                  AND pa.event_type != 'home_run'
                GROUP BY etapa, pa.pitching_team_id
            )
            SELECT
                {etapa_sql} AS etapa,
                CASE WHEN f.team_id = 674 THEN 'Charros de Jalisco' ELSE t.name END AS equipo,
                f.team_id,
                SUM(f.put_outs) AS PO,
                SUM(f.assists) AS A,
                SUM(f.errors) AS E,
                SUM(f.chances) AS chances,
                ROUND(1.0 * (SUM(f.put_outs) + SUM(f.assists)) / NULLIF(SUM(f.chances), 0), 4) AS FPCT,
                b.BIP_total,
                ROUND(100.0 * b.BIP_outs / NULLIF(b.BIP_total, 0), 1) AS "DER%"
            FROM fielding_game_stats f
            JOIN v_valid_games g ON f.game_pk = g.game_pk
            JOIN teams t ON f.team_id = t.team_id
            LEFT JOIN bip b ON b.etapa = ({etapa_sql}) AND b.team_id = f.team_id
            WHERE g.season = 2025
            GROUP BY etapa, f.team_id
        """, _conn)
    return bat_2025_df, fld_2025_df, pit_2025_df, standings_2025_df, yaquis_hist_df


@app.cell
def _(mo):
    etapa_selector = mo.ui.dropdown(
        options=["1ra Vuelta", "2da Vuelta", "Playoffs"],
        value="1ra Vuelta",
        label="Filtrar etapa de la temporada 2025–26:",
    )
    rol_selector = mo.ui.dropdown(
        options=["Abridor", "Relevista"],
        value="Abridor",
        label="Rol de pitcheo:",
    )
    mo.hstack([etapa_selector, rol_selector], justify="start", gap=2)
    return etapa_selector, rol_selector


@app.cell
def _(bat_2025_df, etapa_selector, fld_2025_df, mo, pit_2025_df, rol_selector, standings_2025_df):
    st_view = standings_2025_df[standings_2025_df["etapa"] == etapa_selector.value].sort_values("PCT", ascending=False)
    bat_view = bat_2025_df[bat_2025_df["etapa"] == etapa_selector.value].sort_values("OPS", ascending=False)
    pit_view = pit_2025_df[
        (pit_2025_df["etapa"] == etapa_selector.value) & (pit_2025_df["rol"] == rol_selector.value)
    ].sort_values("ERA", ascending=True)
    fld_view = fld_2025_df[fld_2025_df["etapa"] == etapa_selector.value].sort_values("DER%", ascending=False)

    mo.vstack([
        mo.md(f"## Standings y Diferencial de Carreras ({etapa_selector.value})"),
        mo.ui.table(st_view, selection=None),
        mo.md(f"## Ofensiva por Equipo ({etapa_selector.value})"),
        mo.ui.table(bat_view, selection=None),
        mo.md(f"## Pitcheo — {rol_selector.value} ({etapa_selector.value})"),
        mo.ui.table(pit_view, selection=None),
        mo.md(f"## Defensa y DER% ({etapa_selector.value})"),
        mo.ui.table(fld_view, selection=None),
    ])
    return


@app.cell
def _(mo, yaquis_hist_df):
    mo.vstack([
        mo.md("## Contexto Histórico — Yaquis de Obregón (2006–2026)"),
        mo.ui.table(yaquis_hist_df, selection=None),
    ])
    return


if __name__ == "__main__":
    app.run()
