"""Enriquece web/data/front_office_payload.json con conteos Statcast en pitch_points,
splits completos LHB/RHB/Local/Visita/RISP + últimas 3 salidas + B2B para pitchers,
y preservación situacional en yaquis_batters desde data/yaquis_lmp.db (solo lectura).
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

import build_front_office_data as bfod  # noqa: E402

PAYLOAD_PATH = PROJECT_DIR / "web" / "data" / "front_office_payload.json"
DB_PATH = bfod.DB_PATH
YAQUIS_ID = bfod.YAQUIS_ID


def load_season_frames(conn: sqlite3.Connection, season: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    v1_end = bfod.V1_CUTOFFS.get(season, f"{season}-11-23")
    etapa_sql = f"""
        CASE
            WHEN g.game_stage = 'PLAYOFFS' THEN 'playoffs'
            WHEN g.game_date <= '{v1_end}' THEN 'v1'
            ELSE 'v2'
        END
    """
    games_df = pd.read_sql_query(
        f"""
        SELECT game_pk, season, game_stage, game_date, {etapa_sql} AS etapa,
               home_team_id, away_team_id
        FROM v_valid_games g
        WHERE g.season = {season}
        ORDER BY g.game_date, g.game_pk
        """,
        conn,
    )

    pit_box = pd.read_sql_query(
        f"""
        SELECT p.game_pk, p.team_id, p.player_id, p.games_started, p.outs,
               p.pitches_thrown, p.hits, p.runs, p.earned_runs, p.home_runs,
               p.walks, p.hit_batsmen, p.strikeouts,
               g.game_date, g.game_stage, g.home_team_id, {etapa_sql} AS etapa
        FROM pitching_game_stats p
        JOIN v_valid_games g ON p.game_pk = g.game_pk
        WHERE g.season = {season}
        """,
        conn,
    )
    pit_box["is_home_pit"] = (pit_box["team_id"] == pit_box["home_team_id"]).astype(int)

    pa_raw = pd.read_sql_query(
        f"""
        SELECT pa.id, pa.game_pk, pa.at_bat_index, pa.inning, pa.half_inning,
               pa.batting_team_id, pa.pitching_team_id, pa.batter_id, pa.pitcher_id,
               pa.bat_side, pa.pitch_hand, pa.event_type, pa.is_out, pa.rbi,
               pa.is_risp, pa.home_score_after, pa.away_score_after,
               pa.hit_coord_x, pa.hit_coord_y, pa.hit_trajectory,
               {etapa_sql} AS etapa, g.game_date, g.game_stage, g.home_team_id
        FROM plate_appearances pa
        JOIN v_valid_games g ON pa.game_pk = g.game_pk
        WHERE g.season = {season} AND pa.pitching_team_id = {YAQUIS_ID}
        """,
        conn,
    )
    pa_df = bfod.compute_pa_context(pa_raw) if not pa_raw.empty else pa_raw
    if not pa_df.empty:
        pa_df["is_home_pit"] = (pa_df["pitching_team_id"] == pa_df["home_team_id"]).astype(int)

    # Todos los pitcheos lanzados por Yaquis en la temporada, ordenados por PA y pitch_number para derivar strikes_before exactos
    pitches_df = pd.read_sql_query(
        f"""
        SELECT p.pa_id, p.pitch_number, p.call_code, p.is_strike,
               p.balls_after, p.strikes_after, p.pitch_x, p.pitch_y,
               pa.game_pk, pa.batter_id, pa.pitcher_id, pa.pitching_team_id,
               pa.bat_side, pa.is_risp, {etapa_sql} AS etapa,
               g.game_stage, g.home_team_id
        FROM pitches p
        JOIN plate_appearances pa ON p.pa_id = pa.id
        JOIN v_valid_games g ON pa.game_pk = g.game_pk
        WHERE g.season = {season} AND pa.pitching_team_id = {YAQUIS_ID}
        ORDER BY pa.game_pk, pa.at_bat_index, p.pitch_number
        """,
        conn,
    )
    if not pitches_df.empty:
        pitches_df["strikes_before"] = (
            pitches_df.groupby("pa_id", sort=False)["strikes_after"].shift(1).fillna(0).astype(int)
        )
        pitches_df.loc[pitches_df["pitch_number"] == 1, "strikes_before"] = 0
        pitches_df["count_state"] = np.where(
            pitches_df["pitch_number"] == 1,
            "0-0",
            np.where(pitches_df["strikes_before"] == 2, "2K", "norm"),
        )
        pitches_df["is_swing"] = pitches_df["call_code"].isin(bfod.SWING_CODES)
        pitches_df["is_whiff"] = pitches_df["call_code"].isin(bfod.WHIFF_CODES)
        pitches_df["in_zone"] = (
            pitches_df["pitch_x"].between(bfod.ZONE_X_LO, bfod.ZONE_X_HI)
            & pitches_df["pitch_y"].between(bfod.ZONE_Y_LO, bfod.ZONE_Y_HI)
        )
        pitches_df["out_zone"] = pitches_df["pitch_x"].notna() & (~pitches_df["in_zone"])
        pitches_df["is_home_pit"] = (pitches_df["pitching_team_id"] == pitches_df["home_team_id"]).astype(int)

    return games_df, pit_box, pa_df, pitches_df


def build_enriched_pitch_points(pitches_df: pd.DataFrame) -> list[list]:
    yp_xy = pitches_df[pitches_df["pitch_x"].notna() & pitches_df["pitch_y"].notna()].copy()
    po_pts = yp_xy[yp_xy["etapa"] == "playoffs"]
    reg_pts = yp_xy[yp_xy["etapa"] != "playoffs"]
    if len(reg_pts) > 3200:
        reg_pts = reg_pts.sample(3200, random_state=42)
    yp_sample = pd.concat([po_pts, reg_pts], ignore_index=True)
    # 13 cols: [etapa, pitcher_id, batter_id, px, py, call_code, is_strike, in_zone, pnum, bat_side, is_home, is_risp, count_state]
    return [
        [
            str(r["etapa"]),
            int(r["pitcher_id"]),
            int(r["batter_id"]),
            round(float(r["pitch_x"]), 1),
            round(float(r["pitch_y"]), 1),
            str(r["call_code"] or ""),
            int(r["is_strike"] or 0),
            1 if bool(r["in_zone"]) else 0,
            int(r["pitch_number"] or 1),
            str(r["bat_side"] or ""),
            int(r["is_home_pit"] or 0),
            int(r["is_risp"] or 0),
            str(r["count_state"] or "norm"),
        ]
        for _, r in yp_sample.iterrows()
    ]


def compute_pitcher_split_metrics(
    pp_box: pd.DataFrame | None,
    ppa: pd.DataFrame,
    ppt: pd.DataFrame,
    cfip: float,
) -> dict:
    pa_n = int(len(ppa))
    if pa_n == 0 and (pp_box is None or pp_box.empty):
        return {"PA": 0}

    if pp_box is not None and not pp_box.empty:
        outs = int(pp_box["outs"].sum())
        ip = outs / 3.0
        er = int(pp_box["earned_runs"].sum())
        h = int(pp_box["hits"].sum())
        bb = int(pp_box["walks"].sum())
        hbp = int(pp_box["hit_batsmen"].sum())
        so = int(pp_box["strikeouts"].sum())
        hr = int(pp_box["home_runs"].sum())
        era = round(9.0 * er / ip, 2) if ip > 0 else None
        ab = int(ppa["is_ab"].sum()) if not ppa.empty else 0
    else:
        outs = int(ppa["outs_added"].sum())
        ip = outs / 3.0
        era = None
        h = int(ppa["is_hit"].sum())
        bb = int(ppa["is_bb"].sum())
        hbp = int(ppa["is_hbp"].sum())
        so = int(ppa["is_so"].sum())
        hr = int(ppa["is_hr"].sum())
        ab = int(ppa["is_ab"].sum())

    whip = round((h + bb) / ip, 2) if ip > 0 else None
    k9 = round(9.0 * so / ip, 2) if ip > 0 else None
    bb9 = round(9.0 * bb / ip, 2) if ip > 0 else None
    fip = round(((13 * hr + 3 * (bb + hbp) - 2 * so) / ip) + cfip, 2) if ip > 0 else None
    avg_ag = round(h / ab, 3) if ab > 0 else None
    sf = int(ppa["is_sf"].sum()) if not ppa.empty else 0
    tb = int(ppa["tb"].sum()) if not ppa.empty else 0
    obp_den = ab + bb + hbp + sf
    obp_ag = (h + bb + hbp) / obp_den if obp_den > 0 else None
    slg_ag = tb / ab if ab > 0 else None
    ops_ag = round(obp_ag + slg_ag, 3) if (obp_ag is not None and slg_ag is not None) else None

    tel = bfod.compute_pitch_telemetry(ppt)
    return bfod.clean_records([{
        "PA": pa_n,
        "IP": round(ip, 1),
        "H": h,
        "HR": hr,
        "BB": bb,
        "SO": so,
        "ERA": era,
        "FIP": fip,
        "WHIP": whip,
        "K9": k9,
        "BB9": bb9,
        "AVG_against": avg_ag,
        "OPS_against": ops_ag,
        "Strike_pct": tel.get("Strike_pct"),
        "FPS_pct": tel.get("FPS_pct"),
        "InZone_pct": tel.get("InZone_pct"),
        "Chase_pct": tel.get("Chase_pct"),
        "Whiff_pct": tel.get("Whiff_pct"),
    }])[0]


def enrich_season_bundle(conn: sqlite3.Connection, season: int, season_bundle: dict) -> None:
    games_df, pit_box, pa_df, pitches_df = load_season_frames(conn, season)
    season_bundle["pitch_points"] = build_enriched_pitch_points(pitches_df)

    # Preparar máscaras de etapa y cFIP de liga desde team_benchmarks
    stage_masks = {
        "global_reg": games_df["game_stage"] == "REGULAR",
        "v1": games_df["etapa"] == "v1",
        "v2": games_df["etapa"] == "v2",
        "playoffs": games_df["etapa"] == "playoffs",
    }

    # Calcular cFIP exacto por etapa desde pit_box de toda la liga
    cfip_by_stage = {}
    for stg, gmask in stage_masks.items():
        g_pks = set(games_df.loc[gmask, "game_pk"])
        lg_p = pit_box[pit_box["game_pk"].isin(g_pks)]
        ip_lg = lg_p["outs"].sum() / 3.0
        if ip_lg > 0:
            lg_era = 9.0 * lg_p["earned_runs"].sum() / ip_lg
            cfip_by_stage[stg] = lg_era - (
                (13 * lg_p["home_runs"].sum() + 3 * (lg_p["walks"].sum() + lg_p["hit_batsmen"].sum()) - 2 * lg_p["strikeouts"].sum()) / ip_lg
            )
        else:
            cfip_by_stage[stg] = 3.10

    yaq_box = pit_box[pit_box["team_id"] == YAQUIS_ID].copy()
    yaq_box = yaq_box.sort_values(["game_date", "game_pk"])

    # Enriquecer cada entrada de yaquis_pitchers con splits, last_outings e is_b2b
    for prow in season_bundle.get("yaquis_pitchers", []):
        pid = int(prow["player_id"])
        stg = prow["etapa"]
        g_pks = set(games_df.loc[stage_masks[stg], "game_pk"])
        cfip = cfip_by_stage.get(stg, 3.10)

        p_box_s = yaq_box[(yaq_box["player_id"] == pid) & (yaq_box["game_pk"].isin(g_pks))]
        ppa_s = pa_df[(pa_df["pitcher_id"] == pid) & (pa_df["game_pk"].isin(g_pks))] if not pa_df.empty else pa_df
        ppt_s = pitches_df[(pitches_df["pitcher_id"] == pid) & (pitches_df["game_pk"].isin(g_pks))] if not pitches_df.empty else pitches_df

        splits = {
            "all": compute_pitcher_split_metrics(p_box_s, ppa_s, ppt_s, cfip),
            "home": compute_pitcher_split_metrics(
                p_box_s[p_box_s["is_home_pit"] == 1],
                ppa_s[ppa_s["is_home_pit"] == 1] if not ppa_s.empty else ppa_s,
                ppt_s[ppt_s["is_home_pit"] == 1] if not ppt_s.empty else ppt_s,
                cfip,
            ),
            "away": compute_pitcher_split_metrics(
                p_box_s[p_box_s["is_home_pit"] == 0],
                ppa_s[ppa_s["is_home_pit"] == 0] if not ppa_s.empty else ppa_s,
                ppt_s[ppt_s["is_home_pit"] == 0] if not ppt_s.empty else ppt_s,
                cfip,
            ),
            "vs_lhb": compute_pitcher_split_metrics(
                None,
                ppa_s[ppa_s["bat_side"] == "L"] if not ppa_s.empty else ppa_s,
                ppt_s[ppt_s["bat_side"] == "L"] if not ppt_s.empty else ppt_s,
                cfip,
            ),
            "vs_rhb": compute_pitcher_split_metrics(
                None,
                ppa_s[ppa_s["bat_side"] == "R"] if not ppa_s.empty else ppa_s,
                ppt_s[ppt_s["bat_side"] == "R"] if not ppt_s.empty else ppt_s,
                cfip,
            ),
            "risp": compute_pitcher_split_metrics(
                None,
                ppa_s[ppa_s["is_risp"] == 1] if not ppa_s.empty else ppa_s,
                ppt_s[ppt_s["is_risp"] == 1] if not ppt_s.empty else ppt_s,
                cfip,
            ),
        }
        prow["splits"] = splits

        # Últimas 3 salidas cronológicas de la etapa (o hasta la etapa) + bandera B2B con recencia
        ref_dt_str = bfod.REF_DATES.get((season, stg))
        hist_p = yaq_box[yaq_box["player_id"] == pid]
        if stg != "playoffs":
            hist_p = hist_p[hist_p["game_stage"] == "REGULAR"]
        if ref_dt_str:
            hist_p = hist_p[hist_p["game_date"] <= ref_dt_str]
        else:
            hist_p = p_box_s

        last3_df = hist_p.tail(3)
        last_outings = []
        for _, r in last3_df.iterrows():
            outs_r = int(r["outs"] or 0)
            last_outings.append({
                "date": str(r["game_date"]),
                "ip": f"{outs_r // 3}.{outs_r % 3}",
                "pitches": int(r["pitches_thrown"] or 0),
                "er": int(r["earned_runs"] or 0),
            })
        prow["last_outings"] = last_outings

        rest_d = prow.get("rest_days")
        dates = pd.to_datetime(hist_p["game_date"]).tolist()
        is_b2b = len(dates) >= 2 and int((dates[-1] - dates[-2]).days) <= 1 and (rest_d is not None and rest_d <= 2)
        prow["is_b2b"] = bool(is_b2b)

        p7 = int(prow.get("pitches_7d") or 0)
        p14 = int(prow.get("pitches_14d") or 0)
        a14 = int(prow.get("apps_14d") or 0)
        rol = prow.get("rol", "Bullpen")
        if (
            (rol == "Abridor" and p14 >= 200)
            or (rol == "Bullpen" and (a14 >= 6 or p14 >= 95))
            or (rest_d is not None and rest_d <= 1 and p7 >= 80)
            or (rol == "Bullpen" and is_b2b and p7 >= 45)
        ):
            prow["fatigue_status"] = "CRÍTICO"
        elif (
            (rol == "Abridor" and p14 >= 160)
            or (rol == "Bullpen" and (a14 >= 4 or p14 >= 75))
            or (rol == "Bullpen" and is_b2b)
        ):
            prow["fatigue_status"] = "PRECAUCIÓN"
        else:
            prow["fatigue_status"] = "ÓPTIMO"

    # Preservar situacionales en raíz de cada entrada yaquis_batters (nunca desaparecen al cambiar Condición)
    sit_keys = ("SB", "CS", "SB_pct", "RISP_AVG", "RISP_OPS", "TWO_OUT_RISP_AVG", "LATE_CLOSE_OPS", "HIGH_LEV_OPS")
    for brow in season_bundle.get("yaquis_batters", []):
        all_split = brow.get("splits", {}).get("all", {})
        for k in sit_keys:
            if k in all_split and all_split[k] is not None:
                brow[k] = all_split[k]


def main() -> None:
    if not PAYLOAD_PATH.exists():
        raise FileNotFoundError(f"No existe payload en {PAYLOAD_PATH}")

    payload = json.loads(PAYLOAD_PATH.read_text(encoding="utf-8"))
    with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as conn:
        for s_key in ("2025", "2026"):
            if s_key in payload.get("seasons", {}):
                enrich_season_bundle(conn, int(s_key), payload["seasons"][s_key])

    out_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    PAYLOAD_PATH.write_text(out_json, encoding="utf-8")
    size_mb = len(out_json.encode("utf-8")) / (1024 * 1024)

    for s_key in ("2025", "2026"):
        sb = payload["seasons"][s_key]
        pp = sb["pitch_points"]
        pit = sb["yaquis_pitchers"]
        bat = sb["yaquis_batters"]
        col_lens = sorted({len(r) for r in pp}) if pp else []
        b2b_cnt = sum(1 for p in pit if p.get("is_b2b"))
        has_splits = sum(1 for p in pit if isinstance(p.get("splits"), dict) and "vs_lhb" in p["splits"])
        has_sit = sum(1 for b in bat if "RISP_AVG" in b or "SB" in b)
        print(
            f"Season {s_key}: pitch_points={len(pp)} cols={col_lens} | "
            f"pitchers={len(pit)} splits_ok={has_splits} b2b={b2b_cnt} | "
            f"batters={len(bat)} sit_root={has_sit}"
        )
    print(f"Payload enriquecido OK: {PAYLOAD_PATH} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
