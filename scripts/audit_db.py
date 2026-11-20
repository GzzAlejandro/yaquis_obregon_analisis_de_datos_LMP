from pathlib import Path
import sqlite3
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


def audit_database(db_path: Path = DB_PATH) -> None:
    if not db_path.exists():
        raise FileNotFoundError(f"No se encontró la base de datos en: {db_path}")

    with sqlite3.connect(db_path, timeout=30) as conn:
        print(f"Base de datos auditada: {db_path}\n")

        # 1. Conteo de filas por tabla
        print("=== 1. CONTEO DE FILAS ===")
        for table in TABLES:
            n = pd.read_sql_query(f"SELECT COUNT(*) AS n FROM {table}", conn)["n"].iloc[0]
            print(f"  {table:<22}: {n:>9,}")

        # 2. Tipos de datos e iteración de nulos por tabla y columna
        print("\n=== 2. TIPOS DE DATOS E ITERACIÓN DE NULOS ===")
        null_report = []
        for table in TABLES:
            schema_df = pd.read_sql_query(f"PRAGMA table_info({table})", conn)
            total_rows = pd.read_sql_query(f"SELECT COUNT(*) AS n FROM {table}", conn)["n"].iloc[0]
            df_sample = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 5000", conn)

            for _, col_info in schema_df.iterrows():
                col = col_info["name"]
                sql_type = col_info["type"]
                null_cnt = pd.read_sql_query(
                    f"SELECT COUNT(*) AS n FROM {table} WHERE {col} IS NULL", conn
                )["n"].iloc[0]
                null_pct = (null_cnt / total_rows * 100.0) if total_rows > 0 else 0.0
                pandas_dtype = str(df_sample[col].dtype) if col in df_sample.columns else "N/A"
                null_report.append({
                    "tabla": table,
                    "columna": col,
                    "sql_type": sql_type,
                    "pandas_dtype": pandas_dtype,
                    "filas": total_rows,
                    "nulos": null_cnt,
                    "pct_nulos": round(null_pct, 2),
                })

        report_df = pd.DataFrame(null_report)
        print("  Resumen de tipos de datos por tabla (sql_type -> pandas_dtype):")
        print(report_df[["tabla", "columna", "sql_type", "pandas_dtype"]].to_string(index=False))

        print("\n  Columnas con valores nulos:")
        only_nulls = report_df[report_df["nulos"] > 0]
        if only_nulls.empty:
            print("  Sin valores nulos en ninguna columna.")
        else:
            print(only_nulls.to_string(index=False))

        # 3. Resumen de partidos por temporada, etapa y estado
        print("\n=== 3. JUEGOS POR TEMPORADA / ETAPA / ESTADO ===")
        games_summary = pd.read_sql_query("""
            SELECT season,
                   game_stage,
                   status_detail,
                   is_completed,
                   SUM(CASE WHEN has_pbp THEN 1 ELSE 0 END) AS con_pbp,
                   COUNT(*) AS juegos
            FROM games
            GROUP BY season, game_stage, status_detail, is_completed
            ORDER BY season, game_stage, is_completed DESC
        """, conn)
        print(games_summary.to_string(index=False))

        # 4. Cobertura de coordenadas 2D
        print("\n=== 4. COBERTURA DE COORDENADAS 2D ===")
        coords_summary = pd.read_sql_query("""
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
        """, conn)
        print(coords_summary.to_string(index=False))


if __name__ == "__main__":
    audit_database()
