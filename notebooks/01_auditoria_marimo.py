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
    TABLES = [
        "teams",
        "games",
        "players",
        "batting_game_stats",
        "pitching_game_stats",
        "fielding_game_stats",
        "plate_appearances",
        "pitches",
    ]
    return DB_PATH, TABLES, mo, pd, sqlite3


@app.cell
def _(DB_PATH, mo):
    mo.md(f"""
    # Auditoría de Calidad de Datos — Yaquis de Obregón (LMP)

    Base SQLite conectada: `{DB_PATH}`
    """)
    return


@app.cell
def _(DB_PATH, TABLES, pd, sqlite3):
    with sqlite3.connect(DB_PATH, timeout=30) as _conn:
        counts_rows = []
        schema_rows = []
        for tbl in TABLES:
            total = pd.read_sql_query(f"SELECT COUNT(*) AS n FROM {tbl}", _conn)["n"].iloc[0]
            counts_rows.append({"tabla": tbl, "filas": total})

            info_df = pd.read_sql_query(f"PRAGMA table_info({tbl})", _conn)
            sample_df = pd.read_sql_query(f"SELECT * FROM {tbl} LIMIT 5000", _conn)
            for _, col_meta in info_df.iterrows():
                col = col_meta["name"]
                null_cnt = pd.read_sql_query(
                    f"SELECT COUNT(*) AS n FROM {tbl} WHERE {col} IS NULL", _conn
                )["n"].iloc[0]
                pct = round((null_cnt / total * 100.0), 2) if total > 0 else 0.0
                schema_rows.append({
                    "tabla": tbl,
                    "columna": col,
                    "sql_type": col_meta["type"],
                    "pandas_dtype": str(sample_df[col].dtype) if col in sample_df.columns else "N/A",
                    "filas": total,
                    "nulos": null_cnt,
                    "pct_nulos": pct,
                })

        counts_df = pd.DataFrame(counts_rows)
        audit_df = pd.DataFrame(schema_rows)

        games_df = pd.read_sql_query("""
            SELECT season, game_stage, status_detail, is_completed,
                   SUM(CASE WHEN has_pbp THEN 1 ELSE 0 END) AS con_pbp,
                   COUNT(*) AS juegos
            FROM games
            GROUP BY season, game_stage, status_detail, is_completed
            ORDER BY season, game_stage, is_completed DESC
        """, _conn)

        coords_df = pd.read_sql_query("""
            SELECT g.season,
                   COUNT(pa.id) AS total_pa,
                   SUM(CASE WHEN pa.hit_coord_x IS NOT NULL AND pa.hit_coord_y IS NOT NULL THEN 1 ELSE 0 END) AS pa_con_hit_xy,
                   (SELECT COUNT(*)
                    FROM pitches p
                    JOIN plate_appearances pa2 ON p.pa_id = pa2.id
                    JOIN games g2 ON pa2.game_pk = g2.game_pk
                    WHERE g2.season = g.season) AS total_pitches,
                   (SELECT COUNT(*)
                    FROM pitches p
                    JOIN plate_appearances pa2 ON p.pa_id = pa2.id
                    JOIN games g2 ON pa2.game_pk = g2.game_pk
                    WHERE g2.season = g.season AND p.pitch_x IS NOT NULL AND p.pitch_y IS NOT NULL) AS pitches_con_xy
            FROM plate_appearances pa
            JOIN games g ON pa.game_pk = g.game_pk
            GROUP BY g.season
            ORDER BY g.season
        """, _conn)
    return audit_df, coords_df, counts_df, games_df


@app.cell
def _(counts_df, mo):
    mo.vstack([
        mo.md("## 1. Conteo de filas por tabla"),
        mo.ui.table(counts_df, selection=None),
    ])
    return


@app.cell
def _(TABLES, mo):
    table_selector = mo.ui.dropdown(
        options=["TODAS"] + TABLES,
        value="TODAS",
        label="Filtrar tabla para revisar tipos y nulos:",
    )
    only_nulls_switch = mo.ui.switch(value=False, label="Mostrar solo columnas con nulos")
    mo.hstack([table_selector, only_nulls_switch], justify="start", gap=2)
    return only_nulls_switch, table_selector


@app.cell
def _(audit_df, mo, only_nulls_switch, table_selector):
    filtered_audit = audit_df.copy()
    if table_selector.value != "TODAS":
        filtered_audit = filtered_audit[filtered_audit["tabla"] == table_selector.value]
    if only_nulls_switch.value:
        filtered_audit = filtered_audit[filtered_audit["nulos"] > 0]

    mo.vstack([
        mo.md("## 2. Tipos de datos e iteración de nulos"),
        mo.ui.table(filtered_audit, selection=None),
    ])
    return


@app.cell
def _(coords_df, games_df, mo):
    mo.vstack([
        mo.md("## 3. Resumen de juegos por temporada y etapa"),
        mo.ui.table(games_df, selection=None),
        mo.md("## 4. Cobertura de coordenadas 2D (Batazos y Pitcheos)"),
        mo.ui.table(coords_df, selection=None),
    ])
    return


@app.cell
def _(TABLES, mo):
    preview_table = mo.ui.dropdown(options=TABLES, value="games", label="Inspeccionar primeras 50 filas de:")
    preview_table
    return (preview_table,)


@app.cell
def _(DB_PATH, mo, pd, preview_table, sqlite3):
    with sqlite3.connect(DB_PATH, timeout=30) as _conn:
        preview_df = pd.read_sql_query(f"SELECT * FROM {preview_table.value} LIMIT 50", _conn)
    mo.ui.table(preview_df, selection=None)
    return


if __name__ == "__main__":
    app.run()
