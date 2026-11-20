import base64
import io
import json
import math
import os
import shutil
import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "yaquis_lmp.db"
OUT_DIR = BASE_DIR / "web" / "data"
ASSETS_DIR = BASE_DIR / "web" / "assets"

LOGO_CO_SRC = Path(
    os.environ.get("YAQUIS_LOGO_CO_SRC", str(ASSETS_DIR / "yaquis_co_monogram.png"))
)
LOGO_MASCOT_SRC = Path(
    os.environ.get("YAQUIS_LOGO_MASCOT_SRC", str(ASSETS_DIR / "yaquis_mascot.jpg"))
)

YAQUIS_ID = 680
MEXICALI_ID = 673
V1_CUTOFFS = {2025: "2025-11-23", 2026: "2026-11-23"}
REF_DATES = {
    (2025, "v1"): "2025-11-23",
    (2025, "v2"): "2025-12-30",
    (2025, "global_reg"): "2025-12-30",
    (2025, "playoffs"): "2026-01-05",
    (2026, "global_reg"): "2026-11-15",
    (2026, "v1"): "2026-11-15",
}
LMP_POINTS_10 = [10.0, 9.0, 8.0, 7.0, 6.0, 5.5, 5.0, 4.5, 4.0, 3.5]

# Zona de strike 2D Gameday calibrada empíricamente (percentiles 2%-98% de Called Strikes)
ZONE_X_LO, ZONE_X_HI = 82.0, 134.3
ZONE_Y_LO, ZONE_Y_HI = 115.9, 182.8
ZONE_CX, ZONE_CY = 107.9, 154.1

HITS = {"single", "double", "triple", "home_run"}
NON_AB = {
    "walk", "intent_walk", "hit_by_pitch",
    "sac_fly", "sac_bunt", "sac_fly_double_play", "catcher_interf",
}
DOUBLE_PLAY_EVENTS = {"grounded_into_double_play", "double_play", "strikeout_double_play"}
TB_MAP = {"single": 1, "double": 2, "triple": 3, "home_run": 4}

SWING_CODES = {"S", "W", "M", "F", "L", "T", "O", "R", "X", "D", "E"}
WHIFF_CODES = {"S", "W", "M"}

COUNTRY_FLAGS = {
    "Mexico": "MX",
    "USA": "US",
    "Cuba": "CU",
    "Dominican Republic": "DO",
    "Venezuela": "VE",
    "Panama": "PA",
    "Puerto Rico": "PR",
    "Colombia": "CO",
    "Japan": "JP",
    "Canada": "CA",
    "Curacao": "CW",
    "Nicaragua": "NI",
    "SIN_DATO": "LMP",
}

CHAMPS_MAP = {
    2007: "Campeón",
    2010: "Campeón",
    2011: "Campeón",
    2012: "Campeón",
    2018: "Subcampeón",
}
ROUND_NAMES = {"W": "Serie Final", "L": "Semifinal", "D": "Cuartos de Final"}


def clean_val(v):
    if v is None:
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating, float)):
        if math.isnan(v) or math.isinf(v):
            return None
        return float(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    return v


def clean_records(records: list[dict]) -> list[dict]:
    return [{k: clean_val(v) for k, v in row.items()} for row in records]


def encode_logo_b64(src: Path, dest_name: str, max_px: int = 160, fmt: str = "PNG") -> str:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    dest_path = ASSETS_DIR / dest_name
    if not src.exists():
        src = dest_path
    if not src.exists():
        return ""
    if src.resolve() != dest_path.resolve():
        shutil.copy2(src, dest_path)
    with Image.open(src) as img:
        img = img.convert("RGBA" if fmt == "PNG" else "RGB")
        img.thumbnail((max_px, max_px), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format=fmt, optimize=True)
        mime = "image/png" if fmt == "PNG" else "image/jpeg"
        return f"data:{mime};base64,{base64.b64encode(buf.getvalue()).decode('ascii')}"


def calc_age(birth_date: str | None, ref_year: int = 2026) -> int | None:
    if not birth_date or len(str(birth_date)) < 4:
        return None
    try:
        bd = pd.Timestamp(birth_date)
        ref = pd.Timestamp(f"{ref_year}-11-18")
        return int((ref - bd).days // 365.25)
    except Exception:
        return None


def compute_pa_context(pa_df: pd.DataFrame) -> pd.DataFrame:
    """Calcula outs_before y score_diff_before dentro de cada medio inning sin fuga."""
    pa_df = pa_df.sort_values(["game_pk", "at_bat_index"]).copy()
    is_hit = pa_df["event_type"].isin(HITS).astype(int)
    is_ab = (~pa_df["event_type"].isin(NON_AB)).astype(int)
    is_bb = pa_df["event_type"].isin({"walk", "intent_walk"}).astype(int)
    is_ubb = (pa_df["event_type"] == "walk").astype(int)
    is_hbp = (pa_df["event_type"] == "hit_by_pitch").astype(int)
    is_sf = pa_df["event_type"].isin({"sac_fly", "sac_fly_double_play"}).astype(int)
    is_so = pa_df["event_type"].isin({"strikeout", "strikeout_double_play"}).astype(int)
    is_1b = (pa_df["event_type"] == "single").astype(int)
    is_2b = (pa_df["event_type"] == "double").astype(int)
    is_3b = (pa_df["event_type"] == "triple").astype(int)
    is_hr = (pa_df["event_type"] == "home_run").astype(int)
    tb = pa_df["event_type"].map(TB_MAP).fillna(0).astype(int)

    pa_df["is_hit"] = is_hit
    pa_df["is_ab"] = is_ab
    pa_df["is_bb"] = is_bb
    pa_df["is_ubb"] = is_ubb
    pa_df["is_hbp"] = is_hbp
    pa_df["is_sf"] = is_sf
    pa_df["is_so"] = is_so
    pa_df["is_1b"] = is_1b
    pa_df["is_2b"] = is_2b
    pa_df["is_3b"] = is_3b
    pa_df["is_hr"] = is_hr
    pa_df["tb"] = tb

    outs_added = np.where(
        pa_df["event_type"].isin(DOUBLE_PLAY_EVENTS), 2,
        np.where(pa_df["is_out"] == 1, 1, 0),
    )
    pa_df["outs_added"] = outs_added

    grp_half = pa_df.groupby(["game_pk", "inning", "half_inning"], sort=False)
    pa_df["outs_before"] = grp_half["outs_added"].cumsum().shift(1, fill_value=0)
    # Reiniciar en el primer PA de cada medio inning
    first_in_half = grp_half.cumcount() == 0
    pa_df.loc[first_in_half, "outs_before"] = 0
    pa_df["outs_before"] = pa_df["outs_before"].clip(0, 2)

    grp_game = pa_df.groupby("game_pk", sort=False)
    prev_home = grp_game["home_score_after"].shift(1).fillna(0)
    prev_away = grp_game["away_score_after"].shift(1).fillna(0)
    first_in_game = grp_game.cumcount() == 0
    prev_home = np.where(first_in_game, 0, prev_home)
    prev_away = np.where(first_in_game, 0, prev_away)

    bat_diff_before = np.where(
        pa_df["half_inning"] == "top",
        prev_away - prev_home,
        prev_home - prev_away,
    )
    pa_df["bat_diff_before"] = bat_diff_before
    pa_df["is_2out_risp"] = ((pa_df["is_risp"] == 1) & (pa_df["outs_before"] == 2)).astype(int)
    pa_df["is_late_close"] = ((pa_df["inning"] >= 7) & (np.abs(bat_diff_before) <= 1)).astype(int)
    pa_df["is_high_lev"] = (
        ((pa_df["inning"] >= 7) & (np.abs(bat_diff_before) <= 2))
        | ((pa_df["inning"] >= 6) & (pa_df["is_risp"] == 1) & (np.abs(bat_diff_before) <= 3))
    ).astype(int)
    return pa_df


def agg_batting_from_pa(df: pd.DataFrame, lg_ctx: dict) -> dict:
    pa = len(df)
    if pa == 0:
        return {"PA": 0}
    ab = int(df["is_ab"].sum())
    h = int(df["is_hit"].sum())
    b1 = int(df["is_1b"].sum())
    b2 = int(df["is_2b"].sum())
    b3 = int(df["is_3b"].sum())
    hr = int(df["is_hr"].sum())
    bb = int(df["is_bb"].sum())
    ubb = int(df["is_ubb"].sum())
    hbp = int(df["is_hbp"].sum())
    sf = int(df["is_sf"].sum())
    so = int(df["is_so"].sum())
    tb = int(df["tb"].sum())
    rbi = int(df["rbi"].fillna(0).sum())

    avg = h / ab if ab else None
    obp_den = ab + bb + hbp + sf
    obp = (h + bb + hbp) / obp_den if obp_den else None
    slg = tb / ab if ab else None
    ops = (obp + slg) if (obp is not None and slg is not None) else None
    iso = (slg - avg) if (slg is not None and avg is not None) else None
    babip_den = ab - so - hr + sf
    babip = (h - hr) / babip_den if babip_den > 0 else None

    woba_den = ab + ubb + sf + hbp
    woba = (
        (0.69 * ubb + 0.72 * hbp + 0.89 * b1 + 1.27 * b2 + 1.62 * b3 + 2.10 * hr) / woba_den
        if woba_den > 0 else None
    )
    lg_obp = lg_ctx.get("lg_OBP") or 0.345
    lg_slg = lg_ctx.get("lg_SLG") or 0.370
    lg_woba = lg_ctx.get("lg_wOBA") or 0.320
    lg_r_pa = lg_ctx.get("lg_R_PA") or 0.115
    woba_scale = 1.20

    ops_plus = (100.0 * (obp / lg_obp + slg / lg_slg - 1.0)) if (obp is not None and slg is not None) else None
    wrc_plus = (
        (((woba - lg_woba) / woba_scale + lg_r_pa) / lg_r_pa) * 100.0
        if (woba is not None and lg_r_pa > 0) else None
    )

    return {
        "PA": pa, "AB": ab, "H": h, "2B": b2, "3B": b3, "HR": hr, "RBI": rbi,
        "BB": bb, "SO": so, "TB": tb,
        "AVG": round(avg, 3) if avg is not None else None,
        "OBP": round(obp, 3) if obp is not None else None,
        "SLG": round(slg, 3) if slg is not None else None,
        "OPS": round(ops, 3) if ops is not None else None,
        "OPS_plus": round(ops_plus, 0) if ops_plus is not None else None,
        "wOBA": round(woba, 3) if woba is not None else None,
        "wRC_plus": round(wrc_plus, 0) if wrc_plus is not None else None,
        "ISO": round(iso, 3) if iso is not None else None,
        "BABIP": round(babip, 3) if babip is not None else None,
        "BB_pct": round(bb / pa * 100, 1),
        "K_pct": round(so / pa * 100, 1),
        "BB_K": round(bb / so, 2) if so > 0 else (round(float(bb), 2) if bb > 0 else 0.0),
        "HR_pct": round(hr / pa * 100, 1),
    }


def compute_pitch_telemetry(p_df: pd.DataFrame) -> dict:
    n = len(p_df)
    if n == 0:
        return {"pitches_pbp": 0}
    swings = int(p_df["is_swing"].sum())
    whiffs = int(p_df["is_whiff"].sum())
    in_zone = int(p_df["in_zone"].sum())
    out_zone = int(p_df["out_zone"].sum())
    o_swings = int((p_df["out_zone"] & p_df["is_swing"]).sum())
    fps_df = p_df[p_df["pitch_number"] == 1]
    xy = p_df.dropna(subset=["pitch_x", "pitch_y"])
    return {
        "pitches_pbp": n,
        "Strike_pct": round(p_df["is_strike"].mean() * 100, 1),
        "FPS_pct": round(fps_df["is_strike"].mean() * 100, 1) if len(fps_df) else None,
        "InZone_pct": round(in_zone / len(xy) * 100, 1) if len(xy) else None,
        "Chase_pct": round(o_swings / out_zone * 100, 1) if out_zone > 0 else None,
        "Whiff_pct": round(whiffs / swings * 100, 1) if swings > 0 else None,
        "mean_x": round(xy["pitch_x"].mean(), 1) if len(xy) else None,
        "mean_y": round(xy["pitch_y"].mean(), 1) if len(xy) else None,
        "sd_x": round(xy["pitch_x"].std(ddof=1), 1) if len(xy) > 1 else None,
        "sd_y": round(xy["pitch_y"].std(ddof=1), 1) if len(xy) > 1 else None,
    }


def assign_lmp_points(df_stage: pd.DataFrame) -> dict[int, float]:
    if df_stage.empty:
        return {}
    ordered = df_stage.sort_values(["PCT", "Diff", "RS"], ascending=[False, False, False]).reset_index(drop=True)
    pts = {}
    for idx, row in ordered.iterrows():
        pts[int(row["team_id"])] = LMP_POINTS_10[idx] if idx < len(LMP_POINTS_10) else 3.0
    return pts


def pct_rank_series(series: pd.Series, higher_is_better: bool = True) -> pd.Series:
    valid = series.dropna()
    if valid.empty:
        return pd.Series(50, index=series.index)
    ranks = valid.rank(pct=True, ascending=higher_is_better) * 98 + 1
    out = pd.Series(50.0, index=series.index)
    out.loc[valid.index] = ranks.round(0)
    return out.clip(1, 99).astype(int)


def to_20_80(percentile: int | float | None) -> int:
    if percentile is None or math.isnan(float(percentile)):
        return 50
    raw = 20.0 + float(percentile) * 0.60
    return int(max(20, min(80, round(raw / 5.0) * 5)))


def build_historical_summary(conn: sqlite3.Connection) -> list[dict]:
    games_df = pd.read_sql_query("""
        SELECT game_pk, season, game_stage, game_type, game_date,
               home_team_id, away_team_id, home_score, away_score, has_pbp
        FROM v_valid_games
        ORDER BY season, game_date
    """, conn)

    # Récord anual de Yaquis y ronda máxima
    yaq_mask = (games_df["home_team_id"] == YAQUIS_ID) | (games_df["away_team_id"] == YAQUIS_ID)
    yg = games_df[yaq_mask].copy()
    yg["rf"] = np.where(yg["home_team_id"] == YAQUIS_ID, yg["home_score"], yg["away_score"])
    yg["ra"] = np.where(yg["home_team_id"] == YAQUIS_ID, yg["away_score"], yg["home_score"])
    yg["w"] = (yg["rf"] > yg["ra"]).astype(int)

    bat_yr = pd.read_sql_query("""
        SELECT g.season,
               CASE WHEN b.team_id = 680 THEN 'Yaquis' ELSE 'LMP' END AS grp,
               SUM(b.plate_appearances) AS PA, SUM(b.at_bats) AS AB,
               SUM(b.hits) AS H, SUM(b.total_bases) AS TB,
               SUM(b.walks) AS BB, SUM(b.hit_by_pitch) AS HBP, SUM(b.sac_flies) AS SF
        FROM batting_game_stats b
        JOIN v_valid_games g ON b.game_pk = g.game_pk
        WHERE g.game_stage = 'REGULAR'
        GROUP BY g.season, grp
    """, conn)
    bat_yr["OBP"] = (bat_yr["H"] + bat_yr["BB"] + bat_yr["HBP"]) / (bat_yr["AB"] + bat_yr["BB"] + bat_yr["HBP"] + bat_yr["SF"])
    bat_yr["SLG"] = bat_yr["TB"] / bat_yr["AB"]
    bat_yr["OPS"] = (bat_yr["OBP"] + bat_yr["SLG"]).round(3)

    pit_yr = pd.read_sql_query("""
        SELECT g.season,
               CASE WHEN p.team_id = 680 THEN 'Yaquis' ELSE 'LMP' END AS grp,
               SUM(p.outs) AS outs, SUM(p.earned_runs) AS ER,
               SUM(p.hits) AS H, SUM(p.walks) AS BB, SUM(p.strikeouts) AS SO
        FROM pitching_game_stats p
        JOIN v_valid_games g ON p.game_pk = g.game_pk
        WHERE g.game_stage = 'REGULAR'
        GROUP BY g.season, grp
    """, conn)
    pit_yr["IP"] = pit_yr["outs"] / 3.0
    pit_yr["ERA"] = (9.0 * pit_yr["ER"] / pit_yr["IP"]).round(2)
    pit_yr["WHIP"] = ((pit_yr["H"] + pit_yr["BB"]) / pit_yr["IP"]).round(2)

    pitches_yr = pd.read_sql_query("""
        SELECT g.season,
               COUNT(*) AS pitches_n,
               ROUND(100.0 * AVG(CASE WHEN p.is_strike = 1 THEN 1.0 ELSE 0.0 END), 1) AS Strike_pct,
               ROUND(100.0 * AVG(CASE WHEN p.pitch_x BETWEEN 82.0 AND 134.3 AND p.pitch_y BETWEEN 115.9 AND 182.8 THEN 1.0 ELSE 0.0 END), 1) AS InZone_pct
        FROM pitches p
        JOIN plate_appearances pa ON p.pa_id = pa.id
        JOIN v_valid_games g ON pa.game_pk = g.game_pk
        WHERE pa.pitching_team_id = 680 AND g.season >= 2011 AND p.pitch_x IS NOT NULL
        GROUP BY g.season
    """, conn)

    rows = []
    for season in sorted(games_df["season"].unique(), reverse=True):
        s_reg = yg[(yg["season"] == season) & (yg["game_stage"] == "REGULAR")]
        s_po = yg[(yg["season"] == season) & (yg["game_stage"] == "PLAYOFFS")]
        reg_g = len(s_reg)
        reg_w = int(s_reg["w"].sum())
        reg_l = reg_g - reg_w
        rs = int(s_reg["rf"].sum())
        ra = int(s_reg["ra"].sum())
        reg_pct = round(reg_w / reg_g, 3) if reg_g else None
        pyth = round((rs ** 1.83) / (rs ** 1.83 + ra ** 1.83), 3) if (rs + ra) > 0 else None

        po_g = len(s_po)
        po_w = int(s_po["w"].sum())
        po_l = po_g - po_w
        po_pct = round(po_w / po_g, 3) if po_g else None

        if season in CHAMPS_MAP:
            outcome = CHAMPS_MAP[int(season)]
        elif season == 2026:
            outcome = "En curso (YTD)"
        elif po_g == 0:
            outcome = "Sin Playoffs"
        else:
            types = set(s_po["game_type"].unique())
            if "W" in types:
                outcome = "Serie Final"
            elif "L" in types:
                outcome = "Semifinal"
            else:
                outcome = "Cuartos de Final"

        yb = bat_yr[(bat_yr["season"] == season) & (bat_yr["grp"] == "Yaquis")]
        lb = bat_yr[(bat_yr["season"] == season) & (bat_yr["grp"] == "LMP")]
        yp = pit_yr[(pit_yr["season"] == season) & (pit_yr["grp"] == "Yaquis")]
        lp = pit_yr[(pit_yr["season"] == season) & (pit_yr["grp"] == "LMP")]
        pz = pitches_yr[pitches_yr["season"] == season]

        rows.append({
            "season": int(season),
            "label": f"{season}–{str(season + 1)[-2:]}",
            "reg_G": reg_g, "reg_W": reg_w, "reg_L": reg_l, "reg_PCT": reg_pct,
            "RS": rs, "RA": ra, "Diff": rs - ra, "Pyth_PCT": pyth,
            "po_G": po_g, "po_W": po_w, "po_L": po_l, "po_PCT": po_pct,
            "outcome": outcome,
            "yaq_OPS": float(yb["OPS"].iloc[0]) if len(yb) else None,
            "lmp_OPS": float(lb["OPS"].iloc[0]) if len(lb) else None,
            "yaq_ERA": float(yp["ERA"].iloc[0]) if len(yp) else None,
            "lmp_ERA": float(lp["ERA"].iloc[0]) if len(lp) else None,
            "yaq_WHIP": float(yp["WHIP"].iloc[0]) if len(yp) else None,
            "Strike_pct": float(pz["Strike_pct"].iloc[0]) if len(pz) else None,
            "InZone_pct": float(pz["InZone_pct"].iloc[0]) if len(pz) else None,
            "pitch_tracking_full": int(season) >= 2011,
        })
    return clean_records(rows)


def process_season_bundle(conn: sqlite3.Connection, season: int, players_df: pd.DataFrame) -> dict:
    v1_end = V1_CUTOFFS.get(season, f"{season}-11-23")
    etapa_sql = f"""
        CASE
            WHEN g.game_stage = 'PLAYOFFS' THEN 'playoffs'
            WHEN g.game_date <= '{v1_end}' THEN 'v1'
            ELSE 'v2'
        END
    """
    team_name_sql = lambda tid_col: f"""
        CASE
            WHEN {tid_col} = 674 AND g.season <= 2013 THEN 'Algodoneros de Guasave'
            WHEN {tid_col} = 674 AND g.season >= 2014 THEN 'Charros de Jalisco'
            ELSE t.name
        END
    """

    games_df = pd.read_sql_query(f"""
        SELECT game_pk, season, game_stage, game_type, game_date,
               {etapa_sql} AS etapa,
               home_team_id, away_team_id, home_team_name, away_team_name,
               home_score, away_score
        FROM v_valid_games g
        WHERE g.season = {season}
        ORDER BY g.game_date, g.game_pk
    """, conn)

    bat_box = pd.read_sql_query(f"""
        SELECT b.*, {etapa_sql} AS etapa, g.game_date, g.game_stage,
               g.home_team_id, g.away_team_id,
               {team_name_sql('b.team_id')} AS team_name
        FROM batting_game_stats b
        JOIN v_valid_games g ON b.game_pk = g.game_pk
        JOIN teams t ON b.team_id = t.team_id
        WHERE g.season = {season}
    """, conn)

    pit_box = pd.read_sql_query(f"""
        SELECT p.*, {etapa_sql} AS etapa, g.game_date, g.game_stage,
               g.home_team_id, g.away_team_id,
               {team_name_sql('p.team_id')} AS team_name
        FROM pitching_game_stats p
        JOIN v_valid_games g ON p.game_pk = g.game_pk
        JOIN teams t ON p.team_id = t.team_id
        WHERE g.season = {season}
    """, conn)

    fld_box = pd.read_sql_query(f"""
        SELECT f.*, {etapa_sql} AS etapa, g.game_date, g.game_stage,
               {team_name_sql('f.team_id')} AS team_name
        FROM fielding_game_stats f
        JOIN v_valid_games g ON f.game_pk = g.game_pk
        JOIN teams t ON f.team_id = t.team_id
        WHERE g.season = {season}
    """, conn)

    pa_raw = pd.read_sql_query(f"""
        SELECT pa.*, {etapa_sql} AS etapa, g.game_date, g.game_stage,
               g.home_team_id, g.away_team_id
        FROM plate_appearances pa
        JOIN v_valid_games g ON pa.game_pk = g.game_pk
        WHERE g.season = {season}
    """, conn)
    pa_df = compute_pa_context(pa_raw)
    pa_df["is_home_bat"] = (pa_df["batting_team_id"] == pa_df["home_team_id"]).astype(int)
    pa_df["is_home_pit"] = (pa_df["pitching_team_id"] == pa_df["home_team_id"]).astype(int)

    pitches_df = pd.read_sql_query(f"""
        SELECT p.pa_id, p.pitch_number, p.call_code, p.is_in_play, p.is_strike, p.is_ball,
               p.balls_after, p.strikes_after, p.pitch_x, p.pitch_y,
               pa.game_pk, pa.batter_id, pa.pitcher_id, pa.batting_team_id, pa.pitching_team_id,
               pa.bat_side, pa.pitch_hand, pa.is_risp,
               {etapa_sql} AS etapa, g.game_stage, g.home_team_id
        FROM pitches p
        JOIN plate_appearances pa ON p.pa_id = pa.id
        JOIN v_valid_games g ON pa.game_pk = g.game_pk
        WHERE g.season = {season}
    """, conn)
    pitches_df["is_swing"] = pitches_df["call_code"].isin(SWING_CODES)
    pitches_df["is_whiff"] = pitches_df["call_code"].isin(WHIFF_CODES)
    pitches_df["in_zone"] = (
        pitches_df["pitch_x"].between(ZONE_X_LO, ZONE_X_HI)
        & pitches_df["pitch_y"].between(ZONE_Y_LO, ZONE_Y_HI)
    )
    pitches_df["out_zone"] = pitches_df["pitch_x"].notna() & (~pitches_df["in_zone"])
    pitches_df["is_home_pit"] = (pitches_df["pitching_team_id"] == pitches_df["home_team_id"]).astype(int)

    # Constantes de liga LMP por etapa para OPS+, wRC+, ERA-, FIP, xFIP
    stage_masks = {
        "global_reg": games_df["game_stage"] == "REGULAR",
        "v1": games_df["etapa"] == "v1",
        "v2": games_df["etapa"] == "v2",
        "playoffs": games_df["etapa"] == "playoffs",
    }

    lg_contexts = {}
    for stg, gmask in stage_masks.items():
        g_pks = set(games_df.loc[gmask, "game_pk"])
        b_sub = bat_box[bat_box["game_pk"].isin(g_pks)]
        p_sub = pit_box[pit_box["game_pk"].isin(g_pks)]
        pa_sub = pa_df[pa_df["game_pk"].isin(g_pks)]
        ab = b_sub["at_bats"].sum()
        h = b_sub["hits"].sum()
        bb = b_sub["walks"].sum()
        ibb = b_sub["intentional_walks"].sum()
        ubb = max(0, bb - ibb)
        hbp = b_sub["hit_by_pitch"].sum()
        sf = b_sub["sac_flies"].sum()
        pa_n = b_sub["plate_appearances"].sum()
        r_n = b_sub["runs"].sum()
        tb = b_sub["total_bases"].sum()
        b2 = b_sub["doubles"].sum()
        b3 = b_sub["triples"].sum()
        hr = b_sub["home_runs"].sum()
        b1 = h - b2 - b3 - hr
        lg_obp = (h + bb + hbp) / (ab + bb + hbp + sf) if (ab + bb + hbp + sf) else 0.345
        lg_slg = tb / ab if ab else 0.370
        lg_woba = (0.69 * ubb + 0.72 * hbp + 0.89 * b1 + 1.27 * b2 + 1.62 * b3 + 2.10 * hr) / (ab + ubb + sf + hbp) if (ab + ubb + sf + hbp) else 0.320

        ip = p_sub["outs"].sum() / 3.0
        er = p_sub["earned_runs"].sum()
        p_hr = p_sub["home_runs"].sum()
        p_bb = p_sub["walks"].sum()
        p_hbp = p_sub["hit_batsmen"].sum()
        p_so = p_sub["strikeouts"].sum()
        lg_era = 9.0 * er / ip if ip > 0 else 4.00
        cfip = lg_era - ((13 * p_hr + 3 * (p_bb + p_hbp) - 2 * p_so) / ip) if ip > 0 else 3.10
        fb_n = int(((pa_sub["hit_trajectory"] == "fly_ball") | (pa_sub["event_type"] == "home_run")).sum())
        lg_hr_fb = p_hr / fb_n if fb_n > 0 else 0.08

        # DER promedio por zona en esta etapa
        bip_z = pa_sub[(pa_sub["hit_coord_x"].notna()) & (pa_sub["event_type"] != "home_run")]
        zone_der = {}
        for zcode in ["7", "8", "9"]:
            zsub = bip_z[bip_z["hit_location"] == zcode]
            zone_der[zcode] = float((zsub["is_out"] == 1).mean()) if len(zsub) else 0.47
        inf_sub = bip_z[bip_z["hit_location"].isin(["3", "4", "5", "6"])]
        zone_der["INF"] = float((inf_sub["is_out"] == 1).mean()) if len(inf_sub) else 0.88

        lg_contexts[stg] = {
            "lg_OBP": lg_obp, "lg_SLG": lg_slg, "lg_wOBA": lg_woba,
            "lg_R_PA": (r_n / pa_n) if pa_n else 0.115,
            "lg_ERA": lg_era, "cFIP": cfip, "lg_HR_FB": lg_hr_fb,
            "zone_der": zone_der,
        }

    # Puntos LMP oficiales por equipo (V1 y V2)
    def build_stage_records_table(g_sub: pd.DataFrame) -> pd.DataFrame:
        if g_sub.empty:
            return pd.DataFrame(columns=["team_id", "equipo", "G", "W", "L", "PCT", "RS", "RA", "Diff", "Pyth_PCT", "L10", "Streak"])
        home = g_sub[["game_pk", "game_date", "home_team_id", "home_team_name", "home_score", "away_score"]].rename(
            columns={"home_team_id": "team_id", "home_team_name": "equipo", "home_score": "rf", "away_score": "ra"}
        )
        home["is_home"] = 1
        away = g_sub[["game_pk", "game_date", "away_team_id", "away_team_name", "away_score", "home_score"]].rename(
            columns={"away_team_id": "team_id", "away_team_name": "equipo", "away_score": "rf", "home_score": "ra"}
        )
        away["is_home"] = 0
        tg = pd.concat([home, away], ignore_index=True).sort_values(["team_id", "game_date", "game_pk"])
        tg["w"] = (tg["rf"] > tg["ra"]).astype(int)
        tg["l"] = (tg["rf"] < tg["ra"]).astype(int)

        out = []
        for tid, grp in tg.groupby("team_id"):
            g_n = len(grp)
            w_n = int(grp["w"].sum())
            l_n = int(grp["l"].sum())
            rs = int(grp["rf"].sum())
            ra = int(grp["ra"].sum())
            pct = round(w_n / g_n, 3) if g_n else 0.0
            pyth = round((rs ** 1.83) / (rs ** 1.83 + ra ** 1.83), 3) if (rs + ra) > 0 else 0.5
            last10 = grp.tail(10)
            l10_str = f"{int(last10['w'].sum())}-{int(last10['l'].sum())}"
            # Racha actual
            outcomes = grp["w"].tolist()
            last_res = outcomes[-1]
            cnt = 0
            for val in reversed(outcomes):
                if val == last_res:
                    cnt += 1
                else:
                    break
            streak = f"{'G' if last_res == 1 else 'P'}{cnt}"
            out.append({
                "team_id": int(tid), "equipo": grp["equipo"].iloc[-1],
                "G": g_n, "W": w_n, "L": l_n, "PCT": pct, "RS": rs, "RA": ra,
                "Diff": rs - ra, "Pyth_PCT": pyth, "L10": l10_str, "Streak": streak,
            })
        return pd.DataFrame(out)

    v1_rec = build_stage_records_table(games_df[games_df["etapa"] == "v1"])
    v2_rec = build_stage_records_table(games_df[games_df["etapa"] == "v2"])
    pts_v1 = assign_lmp_points(v1_rec)
    pts_v2 = assign_lmp_points(v2_rec)

    # Benchmarks completos de los 10 equipos por etapa
    team_benchmarks = {}
    for stg, gmask in stage_masks.items():
        g_sub = games_df[gmask]
        if g_sub.empty:
            team_benchmarks[stg] = {"teams": [], "lg": {}}
            continue
        g_pks = set(g_sub["game_pk"])
        rec_df = build_stage_records_table(g_sub)
        lg_ctx = lg_contexts[stg]

        b_sub = bat_box[bat_box["game_pk"].isin(g_pks)]
        p_sub = pit_box[pit_box["game_pk"].isin(g_pks)]
        f_sub = fld_box[fld_box["game_pk"].isin(g_pks)]
        pa_sub = pa_df[pa_df["game_pk"].isin(g_pks)]
        pit_p_sub = pitches_df[pitches_df["game_pk"].isin(g_pks)]

        rows = []
        for _, r in rec_df.iterrows():
            tid = int(r["team_id"])
            tb_df = b_sub[b_sub["team_id"] == tid]
            tp_df = p_sub[p_sub["team_id"] == tid]
            tf_df = f_sub[f_sub["team_id"] == tid]
            tpa_bat = pa_sub[pa_sub["batting_team_id"] == tid]
            tpa_pit = pa_sub[pa_sub["pitching_team_id"] == tid]
            tpitch = pit_p_sub[pit_p_sub["pitching_team_id"] == tid]

            # Bateo
            pa_n = int(tb_df["plate_appearances"].sum())
            ab = int(tb_df["at_bats"].sum())
            h = int(tb_df["hits"].sum())
            b2 = int(tb_df["doubles"].sum())
            b3 = int(tb_df["triples"].sum())
            hr = int(tb_df["home_runs"].sum())
            b1 = h - b2 - b3 - hr
            tot_b = int(tb_df["total_bases"].sum())
            bb = int(tb_df["walks"].sum())
            ibb = int(tb_df["intentional_walks"].sum())
            ubb = max(0, bb - ibb)
            hbp = int(tb_df["hit_by_pitch"].sum())
            sf = int(tb_df["sac_flies"].sum())
            so = int(tb_df["strikeouts"].sum())
            sb = int(tb_df["stolen_bases"].sum())
            cs = int(tb_df["caught_stealing"].sum())

            avg = h / ab if ab else 0
            obp = (h + bb + hbp) / (ab + bb + hbp + sf) if (ab + bb + hbp + sf) else 0
            slg = tot_b / ab if ab else 0
            ops = obp + slg
            woba = (0.69 * ubb + 0.72 * hbp + 0.89 * b1 + 1.27 * b2 + 1.62 * b3 + 2.10 * hr) / (ab + ubb + sf + hbp) if (ab + ubb + sf + hbp) else 0
            ops_plus = 100.0 * (obp / lg_ctx["lg_OBP"] + slg / lg_ctx["lg_SLG"] - 1.0)
            wrc_plus = (((woba - lg_ctx["lg_wOBA"]) / 1.20 + lg_ctx["lg_R_PA"]) / lg_ctx["lg_R_PA"]) * 100.0 if lg_ctx["lg_R_PA"] else 100.0
            babip = (h - hr) / (ab - so - hr + sf) if (ab - so - hr + sf) > 0 else 0

            # Situacional bateo
            risp_s = agg_batting_from_pa(tpa_bat[tpa_bat["is_risp"] == 1], lg_ctx)
            r2_s = agg_batting_from_pa(tpa_bat[tpa_bat["is_2out_risp"] == 1], lg_ctx)
            lc_s = agg_batting_from_pa(tpa_bat[tpa_bat["is_late_close"] == 1], lg_ctx)
            hl_s = agg_batting_from_pa(tpa_bat[tpa_bat["is_high_lev"] == 1], lg_ctx)

            # Pitcheo
            outs = int(tp_df["outs"].sum())
            ip = outs / 3.0
            er = int(tp_df["earned_runs"].sum())
            ra_p = int(tp_df["runs"].sum())
            ph = int(tp_df["hits"].sum())
            pbb = int(tp_df["walks"].sum())
            phbp = int(tp_df["hit_batsmen"].sum())
            pso = int(tp_df["strikeouts"].sum())
            phr = int(tp_df["home_runs"].sum())
            era = 9.0 * er / ip if ip else 0
            era_minus = 100.0 * (era / lg_ctx["lg_ERA"]) if lg_ctx["lg_ERA"] else 100
            fip = ((13 * phr + 3 * (pbb + phbp) - 2 * pso) / ip) + lg_ctx["cFIP"] if ip else 0
            fb_p = int(((tpa_pit["hit_trajectory"] == "fly_ball") | (tpa_pit["event_type"] == "home_run")).sum())
            gb_p = int((tpa_pit["hit_trajectory"] == "ground_ball").sum())
            ld_p = int((tpa_pit["hit_trajectory"] == "line_drive").sum())
            xfip = ((13 * (fb_p * lg_ctx["lg_HR_FB"]) + 3 * (pbb + phbp) - 2 * pso) / ip) + lg_ctx["cFIP"] if ip else fip
            lob_den = ph + pbb + phbp - 1.4 * phr
            lob_pct = max(0.0, min(100.0, ((ph + pbb + phbp - ra_p) / lob_den * 100.0))) if lob_den > 0 else 72.0
            tel = compute_pitch_telemetry(tpitch)

            # Defensa & Espacial
            po = int(tf_df["put_outs"].sum())
            a = int(tf_df["assists"].sum())
            err = int(tf_df["errors"].sum())
            ch = int(tf_df["chances"].sum())
            fpct = (po + a) / ch if ch else 0
            bip = tpa_pit[(tpa_pit["hit_coord_x"].notna()) & (tpa_pit["event_type"] != "home_run")]
            der_pct = (bip["is_out"] == 1).mean() * 100 if len(bip) else 0

            # OAA estimado por zona
            oaa_zones = {}
            for zname, zfilter in [
                ("LF", bip["hit_location"] == "7"),
                ("CF", bip["hit_location"] == "8"),
                ("RF", bip["hit_location"] == "9"),
                ("INF", bip["hit_location"].isin(["3", "4", "5", "6"])),
            ]:
                zb = bip[zfilter]
                zkey = zname if zname == "INF" else ("7" if zname == "LF" else ("8" if zname == "CF" else "9"))
                exp_outs = len(zb) * lg_ctx["zone_der"].get(zkey, 0.5)
                act_outs = int((zb["is_out"] == 1).sum())
                oaa_zones[zname] = {
                    "BIP": int(len(zb)), "Outs": act_outs,
                    "DER_pct": round(act_outs / len(zb) * 100, 1) if len(zb) else None,
                    "OAA_est": round(act_outs - exp_outs, 1),
                }
            tot_oaa = round(sum(v["OAA_est"] for v in oaa_zones.values()), 1)

            c_fld = tf_df[tf_df["position"] == "C"]
            c_cs = int(c_fld["caught_stealing"].sum())
            c_sb = int(c_fld["stolen_bases_allowed"].sum())
            cs_pct = round(c_cs / (c_cs + c_sb) * 100, 1) if (c_cs + c_sb) > 0 else None

            p1 = pts_v1.get(tid, 0.0) if stg in ("v1", "global_reg") else 0.0
            p2 = pts_v2.get(tid, 0.0) if stg in ("v2", "global_reg") else 0.0
            rows.append({
                "team_id": tid, "equipo": r["equipo"],
                "G": int(r["G"]), "W": int(r["W"]), "L": int(r["L"]), "PCT": float(r["PCT"]),
                "RS": int(r["RS"]), "RA": int(r["RA"]), "Diff": int(r["Diff"]), "Pyth_PCT": float(r["Pyth_PCT"]),
                "Pyth_W": int(round(r["Pyth_PCT"] * r["G"])), "Pyth_L": int(r["G"] - round(r["Pyth_PCT"] * r["G"])),
                "L10": r["L10"], "Streak": r["Streak"],
                "Pts_V1": p1, "Pts_V2": p2,
                "Pts_Total": round(p1 + p2, 1) if stg == "global_reg" else (p1 if stg == "v1" else p2),
                # Batting
                "PA": pa_n, "AVG": round(avg, 3), "OBP": round(obp, 3), "SLG": round(slg, 3), "OPS": round(ops, 3),
                "OPS_plus": round(ops_plus, 0), "wOBA": round(woba, 3), "wRC_plus": round(wrc_plus, 0),
                "ISO": round(slg - avg, 3), "BABIP": round(babip, 3),
                "BB_pct": round(bb / pa_n * 100, 1) if pa_n else 0, "K_pct": round(so / pa_n * 100, 1) if pa_n else 0,
                "BB_K": round(bb / so, 2) if so else 0, "HR": hr, "HR_pct": round(hr / pa_n * 100, 1) if pa_n else 0,
                "SB": sb, "CS": cs, "SB_pct": round(sb / (sb + cs) * 100, 1) if (sb + cs) else 0,
                "RISP_AVG": risp_s.get("AVG"), "RISP_OPS": risp_s.get("OPS"),
                "TWO_OUT_RISP_AVG": r2_s.get("AVG"), "LATE_CLOSE_OPS": lc_s.get("OPS"), "HIGH_LEV_OPS": hl_s.get("OPS"),
                # Pitching
                "IP": round(ip, 1), "ERA": round(era, 2), "ERA_minus": round(era_minus, 0),
                "FIP": round(fip, 2), "xFIP": round(xfip, 2),
                "WHIP": round((ph + pbb) / ip, 2) if ip else 0,
                "K9": round(9.0 * pso / ip, 2) if ip else 0, "BB9": round(9.0 * pbb / ip, 2) if ip else 0,
                "K_BB": round(pso / pbb, 2) if pbb else 0, "HR9": round(9.0 * phr / ip, 2) if ip else 0,
                "LOB_pct": round(lob_pct, 1), "GB_FB": round(gb_p / fb_p, 2) if fb_p else None,
                "BIP_GB_pct": round(gb_p / len(bip) * 100, 1) if len(bip) else None,
                "BIP_LD_pct": round(ld_p / len(bip) * 100, 1) if len(bip) else None,
                "BIP_FB_pct": round(fb_p / len(bip) * 100, 1) if len(bip) else None,
                **tel,
                # Defense
                "FPCT": round(fpct, 4), "E": err, "DER_pct": round(der_pct, 1),
                "OAA_est": tot_oaa, "OAA_LF": oaa_zones["LF"]["OAA_est"], "DER_LF": oaa_zones["LF"]["DER_pct"],
                "OAA_CF": oaa_zones["CF"]["OAA_est"], "DER_CF": oaa_zones["CF"]["DER_pct"],
                "OAA_RF": oaa_zones["RF"]["OAA_est"], "DER_RF": oaa_zones["RF"]["DER_pct"],
                "OAA_INF": oaa_zones["INF"]["OAA_est"], "DER_INF": oaa_zones["INF"]["DER_pct"],
                "C_CS_pct": cs_pct,
            })
        tdf = pd.DataFrame(rows)
        # Rankings Yaquis (#1 = mejor)
        ranks = {}
        if not tdf.empty and (tdf["team_id"] == YAQUIS_ID).any():
            for col, asc in [
                ("PCT", False), ("OPS", False), ("wRC_plus", False), ("ERA", True),
                ("FIP", True), ("WHIP", True), ("BB9", True), ("K9", False),
                ("InZone_pct", False), ("DER_pct", False), ("FPCT", False), ("OAA_est", False),
            ]:
                if col in tdf.columns and tdf[col].notna().any():
                    s_rk = tdf[col].rank(ascending=asc, method="min")
                    val = s_rk.loc[tdf["team_id"] == YAQUIS_ID].iloc[0]
                    ranks[col] = int(val) if pd.notna(val) else None

        team_benchmarks[stg] = {
            "teams": clean_records(tdf.sort_values("PCT", ascending=False).to_dict(orient="records")),
            "yaquis_ranks": ranks,
            "lg_ctx": clean_records([lg_ctx])[0],
        }

    # Splits de equipo Yaquis por condición (all, home, away, vs_lhp, vs_rhp, risp) y etapa
    cond_filters = {
        "all": lambda d: d,
        "home": lambda d: d[d["is_home"] == 1],
        "away": lambda d: d[d["is_home"] == 0],
        "vs_lhp": lambda d: d[d["pitch_hand"] == "L"],
        "vs_rhp": lambda d: d[d["pitch_hand"] == "R"],
        "risp": lambda d: d[d["is_risp"] == 1],
    }

    yaquis_team_splits = {}
    for stg, gmask in stage_masks.items():
        g_pks = set(games_df.loc[gmask, "game_pk"])
        lg_ctx = lg_contexts[stg]
        y_bat_pa = pa_df[(pa_df["game_pk"].isin(g_pks)) & (pa_df["batting_team_id"] == YAQUIS_ID)].copy()
        y_bat_pa["is_home"] = y_bat_pa["is_home_bat"]
        y_pit_pa = pa_df[(pa_df["game_pk"].isin(g_pks)) & (pa_df["pitching_team_id"] == YAQUIS_ID)].copy()
        y_pit_pa["is_home"] = y_pit_pa["is_home_pit"]
        y_pit_p = pitches_df[(pitches_df["game_pk"].isin(g_pks)) & (pitches_df["pitching_team_id"] == YAQUIS_ID)].copy()
        y_pit_p["is_home"] = y_pit_p["is_home_pit"]

        yaquis_team_splits[stg] = {}
        for cond, fn in cond_filters.items():
            b_s = agg_batting_from_pa(fn(y_bat_pa), lg_ctx)
            # Pitcheo contra esa condición (para vs_lhp/vs_rhp filtramos por bat_side del rival!)
            if cond == "vs_lhp":
                p_pa_s = y_pit_pa[y_pit_pa["bat_side"] == "L"]
                p_p_s = y_pit_p[y_pit_p["bat_side"] == "L"]
            elif cond == "vs_rhp":
                p_pa_s = y_pit_pa[y_pit_pa["bat_side"] == "R"]
                p_p_s = y_pit_p[y_pit_p["bat_side"] == "R"]
            else:
                p_pa_s = fn(y_pit_pa)
                p_p_s = fn(y_pit_p)

            tel = compute_pitch_telemetry(p_p_s)
            bip_p = p_pa_s[(p_pa_s["hit_coord_x"].notna()) & (p_pa_s["event_type"] != "home_run")]
            outs_p = int(p_pa_s["outs_added"].sum())
            ip_p = outs_p / 3.0
            p_hits = int(p_pa_s["is_hit"].sum())
            p_bb = int(p_pa_s["is_bb"].sum())
            p_so = int(p_pa_s["is_so"].sum())
            p_hr = int(p_pa_s["is_hr"].sum())
            p_hbp = int(p_pa_s["is_hbp"].sum())
            fip_s = ((13 * p_hr + 3 * (p_bb + p_hbp) - 2 * p_so) / ip_p) + lg_ctx["cFIP"] if ip_p > 0 else None

            yaquis_team_splits[stg][cond] = clean_records([{
                **{f"bat_{k}": v for k, v in b_s.items()},
                "pit_PA": len(p_pa_s), "pit_IP": round(ip_p, 1),
                "pit_AVG_against": round(p_hits / p_pa_s["is_ab"].sum(), 3) if p_pa_s["is_ab"].sum() else None,
                "pit_WHIP": round((p_hits + p_bb) / ip_p, 2) if ip_p > 0 else None,
                "pit_K9": round(9.0 * p_so / ip_p, 2) if ip_p > 0 else None,
                "pit_BB9": round(9.0 * p_bb / ip_p, 2) if ip_p > 0 else None,
                "pit_FIP": round(fip_s, 2) if fip_s is not None else None,
                "DER_pct": round((bip_p["is_out"] == 1).mean() * 100, 1) if len(bip_p) else None,
                **tel,
            }])[0]

    # Bateadores individuales de Yaquis (por etapa y condición)
    yaq_bat_box = bat_box[bat_box["team_id"] == YAQUIS_ID]
    yaq_bat_pa = pa_df[pa_df["batting_team_id"] == YAQUIS_ID].copy()
    yaq_bat_pa["is_home"] = yaq_bat_pa["is_home_bat"]
    yaq_batter_ids = sorted(set(yaq_bat_box["player_id"].unique()) | set(yaq_bat_pa["batter_id"].unique()))

    yaquis_batters = []
    for stg, gmask in stage_masks.items():
        g_pks = set(games_df.loc[gmask, "game_pk"])
        if not g_pks:
            continue
        lg_ctx = lg_contexts[stg]
        b_stg = yaq_bat_box[yaq_bat_box["game_pk"].isin(g_pks)]
        pa_stg = yaq_bat_pa[yaq_bat_pa["game_pk"].isin(g_pks)]

        for pid in yaq_batter_ids:
            pb = b_stg[b_stg["player_id"] == pid]
            ppa = pa_stg[pa_stg["batter_id"] == pid]
            if len(pb) == 0 and len(ppa) == 0:
                continue

            # Boxscore base ("all") para exactitud de R, SB, CS, G
            g_cnt = int(pb["game_pk"].nunique())
            r_tot = int(pb["runs"].sum())
            sb_tot = int(pb["stolen_bases"].sum())
            cs_tot = int(pb["caught_stealing"].sum())
            sb_pct = round(sb_tot / (sb_tot + cs_tot) * 100, 1) if (sb_tot + cs_tot) > 0 else None

            risp_sub = agg_batting_from_pa(ppa[ppa["is_risp"] == 1], lg_ctx)
            r2_sub = agg_batting_from_pa(ppa[ppa["is_2out_risp"] == 1], lg_ctx)
            lc_sub = agg_batting_from_pa(ppa[ppa["is_late_close"] == 1], lg_ctx)
            hl_sub = agg_batting_from_pa(ppa[ppa["is_high_lev"] == 1], lg_ctx)

            splits_map = {}
            for cond, fn in cond_filters.items():
                s_res = agg_batting_from_pa(fn(ppa), lg_ctx)
                if cond == "all":
                    s_res.update({
                        "G": g_cnt, "R": r_tot, "SB": sb_tot, "CS": cs_tot, "SB_pct": sb_pct,
                        "RISP_AVG": risp_sub.get("AVG"), "RISP_OPS": risp_sub.get("OPS"),
                        "TWO_OUT_RISP_AVG": r2_sub.get("AVG"),
                        "LATE_CLOSE_OPS": lc_sub.get("OPS"), "HIGH_LEV_OPS": hl_sub.get("OPS"),
                    })
                splits_map[cond] = clean_records([s_res])[0]

            yaquis_batters.append({
                "player_id": int(pid),
                "etapa": stg,
                "splits": splits_map,
            })

    # Lanzadores individuales de Yaquis (por etapa + fatiga 7d/14d/30d)
    yaq_pit_box = pit_box[pit_box["team_id"] == YAQUIS_ID].copy()
    yaq_pit_box["game_date_dt"] = pd.to_datetime(yaq_pit_box["game_date"])
    yaq_pit_pa = pa_df[pa_df["pitching_team_id"] == YAQUIS_ID]
    yaq_pit_p = pitches_df[pitches_df["pitching_team_id"] == YAQUIS_ID]
    yaq_pitcher_ids = sorted(set(yaq_pit_box["player_id"].unique()))

    yaquis_pitchers = []
    for stg, gmask in stage_masks.items():
        g_pks = set(games_df.loc[gmask, "game_pk"])
        if not g_pks:
            continue
        lg_ctx = lg_contexts[stg]
        p_stg = yaq_pit_box[yaq_pit_box["game_pk"].isin(g_pks)]
        pa_stg = yaq_pit_pa[yaq_pit_pa["game_pk"].isin(g_pks)]
        pt_stg = yaq_pit_p[yaq_pit_p["game_pk"].isin(g_pks)]
        ref_dt = pd.Timestamp(REF_DATES.get((season, stg), str(games_df.loc[gmask, "game_date"].max())))

        for pid in yaq_pitcher_ids:
            pp = p_stg[p_stg["player_id"] == pid]
            if pp.empty:
                continue
            ppa = pa_stg[pa_stg["pitcher_id"] == pid]
            ppt = pt_stg[pt_stg["pitcher_id"] == pid]

            outs = int(pp["outs"].sum())
            ip = outs / 3.0
            gs = int(pp["games_started"].sum())
            g_cnt = int(len(pp))
            rol = "Abridor" if gs > 0 and gs >= g_cnt / 2 else "Bullpen"
            er = int(pp["earned_runs"].sum())
            ra_p = int(pp["runs"].sum())
            h = int(pp["hits"].sum())
            bb = int(pp["walks"].sum())
            hbp = int(pp["hit_batsmen"].sum())
            so = int(pp["strikeouts"].sum())
            hr = int(pp["home_runs"].sum())
            era = 9.0 * er / ip if ip > 0 else None
            era_minus = 100.0 * (era / lg_ctx["lg_ERA"]) if (era is not None and lg_ctx["lg_ERA"]) else None
            fip = ((13 * hr + 3 * (bb + hbp) - 2 * so) / ip) + lg_ctx["cFIP"] if ip > 0 else None
            fb = int(((ppa["hit_trajectory"] == "fly_ball") | (ppa["event_type"] == "home_run")).sum())
            gb = int((ppa["hit_trajectory"] == "ground_ball").sum())
            xfip = ((13 * (fb * lg_ctx["lg_HR_FB"]) + 3 * (bb + hbp) - 2 * so) / ip) + lg_ctx["cFIP"] if ip > 0 else fip
            lob_den = h + bb + hbp - 1.4 * hr
            lob_pct = max(0.0, min(100.0, ((h + bb + hbp - ra_p) / lob_den * 100.0))) if lob_den > 0 else None
            tel = compute_pitch_telemetry(ppt)

            # Carga acumulada relativa a ref_dt (usando historial completo de esa temporada hasta ref_dt)
            hist_p = yaq_pit_box[(yaq_pit_box["player_id"] == pid) & (yaq_pit_box["game_date_dt"] <= ref_dt)]
            p7 = int(hist_p[hist_p["game_date_dt"] >= ref_dt - pd.Timedelta(days=6)]["pitches_thrown"].sum())
            p14 = int(hist_p[hist_p["game_date_dt"] >= ref_dt - pd.Timedelta(days=13)]["pitches_thrown"].sum())
            p30 = int(hist_p[hist_p["game_date_dt"] >= ref_dt - pd.Timedelta(days=29)]["pitches_thrown"].sum())
            a7 = int((hist_p["game_date_dt"] >= ref_dt - pd.Timedelta(days=6)).sum())
            a14 = int((hist_p["game_date_dt"] >= ref_dt - pd.Timedelta(days=13)).sum())
            last_dt = hist_p["game_date_dt"].max()
            rest_days = int((ref_dt - last_dt).days) if pd.notna(last_dt) else None

            if (rol == "Abridor" and p14 >= 200) or (rol == "Bullpen" and a14 >= 6) or (rest_days is not None and rest_days <= 1 and p7 >= 80):
                fat_status = "CRÍTICO"
            elif (rol == "Abridor" and p14 >= 160) or (rol == "Bullpen" and a14 >= 4):
                fat_status = "PRECAUCIÓN"
            else:
                fat_status = "ÓPTIMO"

            yaquis_pitchers.append(clean_records([{
                "player_id": int(pid), "etapa": stg, "rol": rol,
                "G": g_cnt, "GS": gs, "W": int(pp["wins"].sum()), "L": int(pp["losses"].sum()),
                "SV": int(pp["saves"].sum()), "HLD": int(pp["holds"].sum()),
                "IP": round(ip, 1), "Pitches": int(pp["pitches_thrown"].sum()),
                "ERA": round(era, 2) if era is not None else None,
                "ERA_minus": round(era_minus, 0) if era_minus is not None else None,
                "FIP": round(fip, 2) if fip is not None else None,
                "xFIP": round(xfip, 2) if xfip is not None else None,
                "WHIP": round((h + bb) / ip, 2) if ip > 0 else None,
                "K9": round(9.0 * so / ip, 2) if ip > 0 else None,
                "BB9": round(9.0 * bb / ip, 2) if ip > 0 else None,
                "K_BB": round(so / bb, 2) if bb > 0 else (float(so) if so > 0 else 0.0),
                "HR9": round(9.0 * hr / ip, 2) if ip > 0 else None,
                "LOB_pct": round(lob_pct, 1) if lob_pct is not None else None,
                "GB_FB": round(gb / fb, 2) if fb > 0 else None,
                "IR": int(pp["inherited_runners"].sum()), "IRS": int(pp["inherited_runners_scored"].sum()),
                "pitches_7d": p7, "pitches_14d": p14, "pitches_30d": p30,
                "apps_7d": a7, "apps_14d": a14,
                "last_date": str(last_dt.date()) if pd.notna(last_dt) else None,
                "rest_days": rest_days, "fatigue_status": fat_status,
                **tel,
            }])[0])

    # Percentiles de la LMP y Escala Scouting 20-80 para el roster completo de Yaquis
    reg_g_pks = set(games_df.loc[games_df["game_stage"] == "REGULAR", "game_pk"])
    min_pa_q = 60 if season == 2025 else 25
    min_ip_q = 15.0 if season == 2025 else 6.0

    # Pool LMP Bateadores
    lmp_b_pool = bat_box[bat_box["game_pk"].isin(reg_g_pks)].groupby("player_id", as_index=False)[
        ["plate_appearances", "at_bats", "hits", "doubles", "triples", "home_runs", "total_bases", "walks", "hit_by_pitch", "sac_flies", "strikeouts", "stolen_bases", "caught_stealing"]
    ].sum()
    lmp_b_pool = lmp_b_pool[lmp_b_pool["plate_appearances"] >= min_pa_q].copy()
    lmp_b_pool["AVG"] = lmp_b_pool["hits"] / lmp_b_pool["at_bats"].replace(0, np.nan)
    lmp_b_pool["OBP"] = (lmp_b_pool["hits"] + lmp_b_pool["walks"] + lmp_b_pool["hit_by_pitch"]) / (lmp_b_pool["at_bats"] + lmp_b_pool["walks"] + lmp_b_pool["hit_by_pitch"] + lmp_b_pool["sac_flies"]).replace(0, np.nan)
    lmp_b_pool["SLG"] = lmp_b_pool["total_bases"] / lmp_b_pool["at_bats"].replace(0, np.nan)
    lmp_b_pool["OPS"] = lmp_b_pool["OBP"] + lmp_b_pool["SLG"]
    lmp_b_pool["ISO"] = lmp_b_pool["SLG"] - lmp_b_pool["AVG"]
    lmp_b_pool["BABIP"] = (lmp_b_pool["hits"] - lmp_b_pool["home_runs"]) / (lmp_b_pool["at_bats"] - lmp_b_pool["strikeouts"] - lmp_b_pool["home_runs"] + lmp_b_pool["sac_flies"]).replace(0, np.nan)
    lmp_b_pool["BB_pct"] = lmp_b_pool["walks"] / lmp_b_pool["plate_appearances"] * 100
    lmp_b_pool["K_pct"] = lmp_b_pool["strikeouts"] / lmp_b_pool["plate_appearances"] * 100
    lmp_b_pool["SB_rate"] = lmp_b_pool["stolen_bases"] / lmp_b_pool["plate_appearances"] * 100

    # Percentiles de todos los bateadores Yaquis (aunque tengan < min_pa_q, evaluados contra la distribución calificada)
    def rank_against_pool(val, pool_series, higher_is_better=True):
        s = pool_series.dropna()
        if pd.isna(val) or s.empty:
            return 50
        if higher_is_better:
            pct = (s < val).mean() * 98 + 1
        else:
            pct = (s > val).mean() * 98 + 1
        return int(max(1, min(99, round(pct))))

    # Pool LMP Pitchers
    lmp_p_pool = pit_box[pit_box["game_pk"].isin(reg_g_pks)].groupby("player_id", as_index=False)[
        ["outs", "earned_runs", "hits", "walks", "hit_batsmen", "strikeouts", "home_runs"]
    ].sum()
    lmp_p_pool["IP"] = lmp_p_pool["outs"] / 3.0
    lmp_p_pool = lmp_p_pool[lmp_p_pool["IP"] >= min_ip_q].copy()
    lmp_p_pool["ERA"] = 9.0 * lmp_p_pool["earned_runs"] / lmp_p_pool["IP"]
    lmp_p_pool["WHIP"] = (lmp_p_pool["hits"] + lmp_p_pool["walks"]) / lmp_p_pool["IP"]
    lmp_p_pool["K9"] = 9.0 * lmp_p_pool["strikeouts"] / lmp_p_pool["IP"]
    lmp_p_pool["BB9"] = 9.0 * lmp_p_pool["walks"] / lmp_p_pool["IP"]
    lmp_p_pool["HR9"] = 9.0 * lmp_p_pool["home_runs"] / lmp_p_pool["IP"]
    cfip_reg = lg_contexts["global_reg"]["cFIP"]
    lmp_p_pool["FIP"] = ((13 * lmp_p_pool["home_runs"] + 3 * (lmp_p_pool["walks"] + lmp_p_pool["hit_batsmen"]) - 2 * lmp_p_pool["strikeouts"]) / lmp_p_pool["IP"]) + cfip_reg

    # Telemetría LMP por pitcher para percentiles Whiff%, Chase%, InZone%
    lmp_pt_reg = pitches_df[pitches_df["game_stage"] == "REGULAR"].groupby("pitcher_id").agg(
        n=("pitch_number", "count"),
        swings=("is_swing", "sum"),
        whiffs=("is_whiff", "sum"),
        in_z=("in_zone", "sum"),
        out_z=("out_zone", "sum"),
        o_swings=("is_swing", lambda s: int((s & pitches_df.loc[s.index, "out_zone"]).sum())),
        xy_n=("pitch_x", lambda s: int(s.notna().sum())),
    ).reset_index()
    lmp_pt_reg = lmp_pt_reg[lmp_pt_reg["pitcher_id"].isin(lmp_p_pool["player_id"])].copy()
    lmp_pt_reg["Whiff_pct"] = lmp_pt_reg["whiffs"] / lmp_pt_reg["swings"].replace(0, np.nan) * 100
    lmp_pt_reg["Chase_pct"] = lmp_pt_reg["o_swings"] / lmp_pt_reg["out_z"].replace(0, np.nan) * 100
    lmp_pt_reg["InZone_pct"] = lmp_pt_reg["in_z"] / lmp_pt_reg["xy_n"].replace(0, np.nan) * 100
    lmp_p_pool = lmp_p_pool.merge(lmp_pt_reg[["pitcher_id", "Whiff_pct", "Chase_pct", "InZone_pct"]], left_on="player_id", right_on="pitcher_id", how="left")

    # Fildeo Yaquis regular por jugador
    yaq_fld_reg = fld_box[(fld_box["team_id"] == YAQUIS_ID) & (fld_box["game_stage"] == "REGULAR")]
    fld_by_p = yaq_fld_reg.groupby("player_id", as_index=False).agg(
        PO=("put_outs", "sum"), A=("assists", "sum"), E=("errors", "sum"), chances=("chances", "sum"),
        positions=("position", lambda s: sorted({str(x) for x in s if x and x != "SIN_DATO"})),
    )
    fld_by_p["FPCT"] = np.where(fld_by_p["chances"] > 0, (fld_by_p["PO"] + fld_by_p["A"]) / fld_by_p["chances"], np.nan)

    p_lookup = players_df.set_index("player_id").to_dict(orient="index")
    bat_reg_map = {r["player_id"]: r for r in yaquis_batters if r["etapa"] == "global_reg"}
    pit_reg_map = {r["player_id"]: r for r in yaquis_pitchers if r["etapa"] == "global_reg"}
    fld_map = fld_by_p.set_index("player_id").to_dict(orient="index")

    roster_ids = sorted(set(yaq_batter_ids) | set(yaq_pitcher_ids))
    scouting_profiles = []
    for pid in roster_ids:
        meta = p_lookup.get(pid, {})
        b_info = bat_reg_map.get(pid)
        p_info = pit_reg_map.get(pid)
        f_info = fld_map.get(pid, {})
        is_pitcher = p_info is not None and (b_info is None or p_info["IP"] >= 2.0)

        country = meta.get("birth_country") or "SIN_DATO"
        age = calc_age(meta.get("birth_date"))
        if country == "Mexico":
            roster_status = "Novato" if (age is not None and age <= 23) else "Nacional"
        elif country == "SIN_DATO":
            roster_status = "Sin Registro"
        else:
            roster_status = "Extranjero"

        name = meta.get("full_name") or f"Jugador {pid}"
        initials = "".join([part[0] for part in name.split()[:2]]).upper()

        if is_pitcher:
            role_group = p_info["rol"]
            pcts = {
                "ERA": rank_against_pool(p_info["ERA"], lmp_p_pool["ERA"], higher_is_better=False),
                "FIP": rank_against_pool(p_info["FIP"], lmp_p_pool["FIP"], higher_is_better=False),
                "WHIP": rank_against_pool(p_info["WHIP"], lmp_p_pool["WHIP"], higher_is_better=False),
                "K9": rank_against_pool(p_info["K9"], lmp_p_pool["K9"], higher_is_better=True),
                "BB9": rank_against_pool(p_info["BB9"], lmp_p_pool["BB9"], higher_is_better=False),
                "HR9": rank_against_pool(p_info["HR9"], lmp_p_pool["HR9"], higher_is_better=False),
                "InZone%": rank_against_pool(p_info.get("InZone_pct"), lmp_p_pool["InZone_pct"], higher_is_better=True),
                "Whiff%": rank_against_pool(p_info.get("Whiff_pct"), lmp_p_pool["Whiff_pct"], higher_is_better=True),
                "Chase%": rank_against_pool(p_info.get("Chase_pct"), lmp_p_pool["Chase_pct"], higher_is_better=True),
            }
            tools_20_80 = {
                "Dominio (K/Whiff)": to_20_80((pcts["K9"] + pcts["Whiff%"]) / 2),
                "Comando (BB/Zona)": to_20_80((pcts["BB9"] + pcts["InZone%"]) / 2),
                "Engaño (Chase%)": to_20_80(pcts["Chase%"]),
                "Supresión (HR/FIP)": to_20_80((pcts["HR9"] + pcts["FIP"]) / 2),
                "Resistencia (Carga)": to_20_80(min(99, p_info["IP"] / (75.0 if role_group == "Abridor" else 35.0) * 90)),
            }
            note = (
                f"{role_group} ({meta.get('pitch_hand') or 'R'}HP) con {p_info['IP']} IP, "
                f"{p_info['ERA']} ERA ({p_info['FIP']} FIP) y {p_info['K9']} K/9 vs {p_info['BB9']} BB/9. "
                f"InZone% {p_info.get('InZone_pct') or '—'}%, Whiff% {p_info.get('Whiff_pct') or '—'}%. "
                f"Carga reciente 14d: {p_info['pitches_14d']} pitcheos ({p_info['fatigue_status']})."
            )
        else:
            bs = (b_info or {}).get("splits", {}).get("all", {})
            role_group = "Bateador"
            pcts = {
                "AVG": rank_against_pool(bs.get("AVG"), lmp_b_pool["AVG"], True),
                "OBP": rank_against_pool(bs.get("OBP"), lmp_b_pool["OBP"], True),
                "SLG": rank_against_pool(bs.get("SLG"), lmp_b_pool["SLG"], True),
                "OPS": rank_against_pool(bs.get("OPS"), lmp_b_pool["OPS"], True),
                "ISO": rank_against_pool(bs.get("ISO"), lmp_b_pool["ISO"], True),
                "BB%": rank_against_pool(bs.get("BB_pct"), lmp_b_pool["BB_pct"], True),
                "K%": rank_against_pool(bs.get("K_pct"), lmp_b_pool["K_pct"], False),
                "BABIP": rank_against_pool(bs.get("BABIP"), lmp_b_pool["BABIP"], True),
                "Velocidad (SB)": rank_against_pool((bs.get("SB", 0) / bs.get("PA", 1) * 100) if bs.get("PA") else 0, lmp_b_pool["SB_rate"], True),
            }
            fld_score = 55 if (f_info.get("FPCT") or 0) >= 0.985 else (45 if (f_info.get("FPCT") or 1) < 0.965 else 50)
            tools_20_80 = {
                "Contacto (Hit)": to_20_80((pcts["AVG"] + pcts["K%"]) / 2),
                "Poder (ISO/SLG)": to_20_80((pcts["ISO"] + pcts["SLG"]) / 2),
                "Disciplina (BB%)": to_20_80(pcts["BB%"]),
                "Velocidad (Run)": to_20_80(pcts["Velocidad (SB)"]),
                "Guante (Field)": fld_score,
            }
            note = (
                f"Perfil {meta.get('primary_position') or 'UT'} ({meta.get('bat_side') or 'R'}/{meta.get('pitch_hand') or 'R'}): "
                f"{bs.get('PA', 0)} PA en rol regular con línea {bs.get('AVG', '—')}/{bs.get('OBP', '—')}/{bs.get('SLG', '—')} "
                f"(OPS {bs.get('OPS', '—')}, wRC+ {bs.get('wRC_plus', '—')}). "
                f"Situacional RISP: {bs.get('RISP_AVG', '—')} AVG."
            )

        sec_pos = [p for p in f_info.get("positions", []) if p != meta.get("primary_position")]
        scouting_profiles.append(clean_records([{
            "player_id": int(pid),
            "full_name": name,
            "initials": initials,
            "role_group": role_group,
            "is_pitcher": bool(is_pitcher),
            "primary_position": meta.get("primary_position") or "SIN_DATO",
            "secondary_positions": sec_pos,
            "age": age,
            "birth_date": meta.get("birth_date"),
            "height": meta.get("height") or "SIN_DATO",
            "weight": meta.get("weight"),
            "bat_side": meta.get("bat_side") or "SIN_DATO",
            "pitch_hand": meta.get("pitch_hand") or "SIN_DATO",
            "birth_country": country,
            "birth_city": meta.get("birth_city") or "SIN_DATO",
            "flag_code": COUNTRY_FLAGS.get(country, "LMP"),
            "roster_status": roster_status,
            "headshot_url": meta.get("headshot_url") or "",
            "percentiles": pcts,
            "tools_20_80": tools_20_80,
            "scout_note": note,
            "reg_pa": (b_info or {}).get("splits", {}).get("all", {}).get("PA", 0),
            "reg_ip": (p_info or {}).get("IP", 0.0),
        }])[0])

    # Ordenar perfiles por protagonismo (PA + IP*4)
    scouting_profiles.sort(key=lambda x: (x["reg_pa"] + x["reg_ip"] * 4), reverse=True)

    # Puntos compactos para Spray Chart 2D (todos los BIP de Yaquis bateando y defendiendo)
    spray_sub = pa_df[
        (pa_df["hit_coord_x"].notna()) & (pa_df["hit_coord_y"].notna())
        & ((pa_df["batting_team_id"] == YAQUIS_ID) | (pa_df["pitching_team_id"] == YAQUIS_ID))
    ].copy()
    # [etapa, is_def, batter_id, pitcher_id, x, y, loc, traj, hard, ev, is_out, bat_side, pitch_hand, is_risp, is_home]
    spray_points = [
        [
            r["etapa"],
            1 if int(r["pitching_team_id"]) == YAQUIS_ID else 0,
            int(r["batter_id"]),
            int(r["pitcher_id"]),
            round(float(r["hit_coord_x"]), 1),
            round(float(r["hit_coord_y"]), 1),
            str(r["hit_location"] or ""),
            str(r["hit_trajectory"] or ""),
            str(r["hit_hardness"] or ""),
            str(r["event_type"] or ""),
            int(r["is_out"] or 0),
            str(r["bat_side"] or ""),
            str(r["pitch_hand"] or ""),
            int(r["is_risp"] or 0),
            int(r["is_home_bat"] if int(r["batting_team_id"]) == YAQUIS_ID else r["is_home_pit"]),
        ]
        for _, r in spray_sub.iterrows()
    ]

    # Puntos compactos de Zona de Strike 2D (pitcheo de Yaquis; todos en playoffs, muestra estratificada hasta 3,000 en reg)
    yp_xy = pitches_df[(pitches_df["pitching_team_id"] == YAQUIS_ID) & (pitches_df["pitch_x"].notna()) & (pitches_df["pitch_y"].notna())].copy()
    po_pts = yp_xy[yp_xy["etapa"] == "playoffs"]
    reg_pts = yp_xy[yp_xy["etapa"] != "playoffs"]
    if len(reg_pts) > 3200:
        reg_pts = reg_pts.sample(3200, random_state=42)
    yp_sample = pd.concat([po_pts, reg_pts], ignore_index=True)

    # [etapa, pitcher_id, batter_id, px, py, call_code, is_strike, in_zone, pnum, bat_side, is_home]
    pitch_points = [
        [
            r["etapa"],
            int(r["pitcher_id"]),
            int(r["batter_id"]),
            round(float(r["pitch_x"]), 1),
            round(float(r["pitch_y"]), 1),
            str(r["call_code"] or ""),
            int(r["is_strike"] or 0),
            1 if r["in_zone"] else 0,
            int(r["pitch_number"] or 1),
            str(r["bat_side"] or ""),
            int(r["is_home_pit"]),
        ]
        for _, r in yp_sample.iterrows()
    ]

    # Juegos recientes / Playoffs serie detalle
    games_summary = clean_records(games_df.tail(20).to_dict(orient="records"))

    return {
        "season": int(season),
        "team_benchmarks": team_benchmarks,
        "yaquis_team_splits": yaquis_team_splits,
        "yaquis_batters": yaquis_batters,
        "yaquis_pitchers": yaquis_pitchers,
        "scouting_profiles": scouting_profiles,
        "spray_points": spray_points,
        "pitch_points": pitch_points,
        "recent_games": games_summary,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as conn:
        players_df = pd.read_sql_query("SELECT * FROM players", conn)
        historical = build_historical_summary(conn)
        s2025 = process_season_bundle(conn, 2025, players_df)
        s2026 = process_season_bundle(conn, 2026, players_df)

    payload = {
        "meta": {
            "club": "Yaquis de Ciudad Obregón",
            "league": "Liga Mexicana del Pacífico (LMP)",
            "championships": [1966, 1973, 1981, 2008, 2011, 2012, 2013],
            "zone_calibration": {
                "x_lo": ZONE_X_LO, "x_hi": ZONE_X_HI,
                "y_lo": ZONE_Y_LO, "y_hi": ZONE_Y_HI,
                "cx": ZONE_CX, "cy": ZONE_CY,
            },
            "logos": {
                "co_monogram": encode_logo_b64(LOGO_CO_SRC, "yaquis_co_monogram.png", max_px=128, fmt="PNG"),
                "mascot": encode_logo_b64(LOGO_MASCOT_SRC, "yaquis_mascot.jpg", max_px=180, fmt="JPEG"),
            },
        },
        "historical_seasons": historical,
        "seasons": {
            "2025": s2025,
            "2026": s2026,
        },
    }

    # Preservar e inyectar logotipos LMP y fotografías locales descargadas si existen en web/assets/
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from fetch_visual_assets import inject_cached_visual_assets
        inject_cached_visual_assets(payload)
    except Exception as exc:
        print(f"Aviso al fusionar activos cacheados: {exc}")

    out_path = OUT_DIR / "front_office_payload.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    size_kb = out_path.stat().st_size / 1024
    print(f"Payload generado en: {out_path} ({size_kb:.1f} KB)")
    print(f"Histórico: {len(historical)} temporadas | S2025 profiles={len(s2025['scouting_profiles'])}, spray={len(s2025['spray_points'])}, pitches={len(s2025['pitch_points'])}")
    print(f"S2026 profiles={len(s2026['scouting_profiles'])}, spray={len(s2026['spray_points'])}, pitches={len(s2026['pitch_points'])}")


if __name__ == "__main__":
    main()
