from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "yaquis_lmp.db"


def clean_database(db_path: Path = DB_PATH) -> None:
    with sqlite3.connect(db_path, timeout=30) as conn:
        cur = conn.cursor()

        # 1. Validar que los IDs de equipo colados en players (674..678) no tengan actividad real
        real_pit = cur.execute("""
            SELECT COUNT(*) FROM pitching_game_stats
            WHERE player_id IN (674, 675, 676, 677, 678)
              AND (outs > 0 OR batters_faced > 0 OR pitches_thrown > 0)
        """).fetchone()[0]
        real_fld = cur.execute("""
            SELECT COUNT(*) FROM fielding_game_stats
            WHERE player_id IN (674, 675, 676, 677, 678)
              AND (chances > 0 OR games_started > 0 OR passed_balls > 0)
        """).fetchone()[0]

        if real_pit == 0 and real_fld == 0:
            cur.execute("DELETE FROM pitching_game_stats WHERE player_id IN (674, 675, 676, 677, 678)")
            cur.execute("DELETE FROM fielding_game_stats WHERE player_id IN (674, 675, 676, 677, 678)")
            cur.execute("DELETE FROM players WHERE player_id IN (674, 675, 676, 677, 678)")
            print("Eliminados 5 registros fantasma de equipos en players/pitching/fielding.")
        else:
            raise ValueError(f"Alerta: actividad real detectada en 674..678 (pit={real_pit}, fld={real_fld})")

        # 2. Etiquetar equipo 58 (cruces futuros de playoffs 2026-27) y unificar Tucson (6484) -> Mayos de Navojoa
        cur.execute("""
            UPDATE teams
            SET name = 'Por Definir (Playoffs)', abbreviation = 'TBD', team_code = 'tbd'
            WHERE team_id = 58
        """)
        cur.execute("""
            UPDATE teams
            SET name = 'Mayos de Navojoa', abbreviation = 'NAV', team_code = 'nav'
            WHERE team_id = 6484
        """)

        # 3. Etiquetar micro-nulos restantes sin perder filas
        cur.execute("""
            UPDATE players
            SET full_name = CASE WHEN full_name IS NULL OR TRIM(full_name) = '' THEN 'SIN_DATO' ELSE full_name END,
                bat_side = COALESCE(bat_side, 'SIN_DATO'),
                pitch_hand = COALESCE(pitch_hand, 'SIN_DATO'),
                primary_position = COALESCE(primary_position, 'SIN_DATO')
            WHERE bat_side IS NULL OR pitch_hand IS NULL OR primary_position IS NULL
               OR full_name IS NULL OR TRIM(full_name) = ''
        """)
        cur.execute("""
            UPDATE fielding_game_stats
            SET position = COALESCE(position, 'SIN_DATO')
            WHERE position IS NULL
        """)
        cur.execute("""
            UPDATE plate_appearances
            SET event = COALESCE(event, 'JUGADA_INCOMPLETA'),
                event_type = COALESCE(event_type, 'JUGADA_INCOMPLETA')
            WHERE event IS NULL OR event_type IS NULL
        """)

        # 4. Vista SQL limpia de juegos válidos + resolución histórica de nombres (674: Algodoneros <=2013 / Charros >=2014; 6484/676: Mayos de Navojoa)
        cur.execute("DROP VIEW IF EXISTS v_valid_games;")
        cur.execute("""
            CREATE VIEW v_valid_games AS
            SELECT
                g.*,
                CASE
                    WHEN g.home_team_id = 674 AND g.season <= 2013 THEN 'Algodoneros de Guasave'
                    WHEN g.home_team_id = 674 AND g.season >= 2014 THEN 'Charros de Jalisco'
                    WHEN g.home_team_id IN (676, 6484) THEN 'Mayos de Navojoa'
                    ELSE th.name
                END AS home_team_name,
                CASE
                    WHEN g.away_team_id = 674 AND g.season <= 2013 THEN 'Algodoneros de Guasave'
                    WHEN g.away_team_id = 674 AND g.season >= 2014 THEN 'Charros de Jalisco'
                    WHEN g.away_team_id IN (676, 6484) THEN 'Mayos de Navojoa'
                    ELSE ta.name
                END AS away_team_name
            FROM games g
            JOIN teams th ON g.home_team_id = th.team_id
            JOIN teams ta ON g.away_team_id = ta.team_id
            WHERE g.is_completed = 1
              AND g.home_score IS NOT NULL
              AND g.away_score IS NOT NULL
              AND g.status_detail != 'Cancelled'
              AND (g.status_detail != 'Postponed' OR g.has_pbp = 1);
        """)

        conn.commit()
        print("Limpieza y vista v_valid_games creadas correctamente.")


if __name__ == "__main__":
    clean_database()
