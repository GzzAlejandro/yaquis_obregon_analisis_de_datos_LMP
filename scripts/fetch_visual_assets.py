"""Downloads and caches official LMP team logos and Yaquis roster player headshots locally,
and injects Base64 Data URIs into web/data/front_office_payload.json for offline/CSP-safe rendering.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import math
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps

BASE_DIR = Path(__file__).resolve().parent.parent
PAYLOAD_PATH = BASE_DIR / "web" / "data" / "front_office_payload.json"
ASSETS_DIR = BASE_DIR / "web" / "assets"
TEAMS_DIR = ASSETS_DIR / "teams"
PLAYERS_DIR = ASSETS_DIR / "players"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) YaquisFrontOfficeR&D/1.0"

TEAM_PNG_CODES: dict[int, str] = {
    680: "OBR",
    675: "MOC",
    673: "MXC",
    677: "HER",
    678: "CUL",
    679: "MAZ",
    674: "JAL",
    5482: "GSV",
    676: "NAV",
    6483: "NAY",
    6484: "NAV",
}

ALL_TEAM_IDS: list[int] = [673, 674, 675, 676, 677, 678, 679, 680, 5482, 6483, 6484]

EXTRA_BRAND_URLS: dict[str, tuple[str, str]] = {
    "lmp_shield": (
        "https://www.lmp.mx/assets/img/icons/fav/apple-icon-180x180.png",
        "lmp_shield.png",
    ),
    "yaquis_wordmark": (
        "https://www.yaquis.com.mx/img/logo-yaquis.png",
        "yaquis_wordmark.png",
    ),
}


def http_get_bytes(url: str, timeout: float = 15.0) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return resp.read()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return None
    return None


def resolve_taiki_sekine_url() -> str | None:
    api_url = (
        "https://en.wikipedia.org/w/api.php?action=query&titles=Taiki_Sekine"
        "&prop=pageimages&pithumbsize=300&format=json"
    )
    raw = http_get_bytes(api_url)
    if not raw:
        return None
    try:
        data = json.loads(raw.decode("utf-8"))
        pages = data.get("query", {}).get("pages", {})
        for p in pages.values():
            src = p.get("thumbnail", {}).get("source")
            if src:
                return src
    except (json.JSONDecodeError, AttributeError):
        return None
    return None


def has_true_alpha(im: Image.Image) -> bool:
    return im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)


def is_generic_silhouette(im: Image.Image, raw_bytes: bytes, generic_hashes: set[str]) -> bool:
    digest = hashlib.sha256(raw_bytes).hexdigest()
    if digest in generic_hashes:
        return True
    thumb = im.convert("RGBA").copy()
    thumb.thumbnail((96, 96), Image.Resampling.BILINEAR)
    px_iter = thumb.get_flattened_data() if hasattr(thumb, "get_flattened_data") else thumb.getdata()
    opaque = [px for px in px_iter if px[3] > 20]
    if not opaque:
        return True
    colored = sum(1 for r, g, b, _ in opaque if (max(r, g, b) - min(r, g, b)) >= 18)
    return (colored / len(opaque)) < 0.12


def _make_yaquis_studio_bg(w: int, h: int) -> Image.Image:
    """Genera un fondo suave de estudio Yaquis (#184270 centro superior -> #0B1B31 bordes)."""
    cx, cy = w * 0.5, h * 0.34
    max_d = math.hypot(w * 0.65, h * 0.72)
    r0, g0, b0 = 24, 66, 112   # #184270
    r1, g1, b1 = 11, 27, 49    # #0B1B31
    pixels: list[tuple[int, int, int]] = []
    for y in range(h):
        dy = y - cy
        for x in range(w):
            t = min(1.0, math.hypot(x - cx, dy) / max_d)
            r = int(r0 + (r1 - r0) * t)
            g = int(g0 + (g1 - g0) * t)
            b = int(b0 + (b1 - b0) * t)
            pixels.append((r, g, b))
    bg = Image.new("RGB", (w, h))
    bg.putdata(pixels)
    return bg


def process_player_portrait(
    raw_bytes: bytes, target_w: int = 176, target_h: int = 220, quality: int = 82
) -> bytes:
    """Preserva encuadre retrato 4:5 (cabeza, gorra con aire, barbilla y hombros).
    Siluetas con canal alfa se componen sobre fondo de estudio Yaquis sin márgenes blancos."""
    im = Image.open(io.BytesIO(raw_bytes))
    im = ImageOps.exif_transpose(im)

    if has_true_alpha(im):
        rgba = im.convert("RGBA")
        alpha = rgba.split()[3]
        bbox = alpha.getbbox()
        if bbox:
            rgba = rgba.crop(bbox)
        bw, bh = rgba.size
        max_w = int(target_w * 0.94)
        max_h = int(target_h * 0.89)
        scale = min(max_w / max(1, bw), max_h / max(1, bh))
        new_w = max(1, int(round(bw * scale)))
        new_h = max(1, int(round(bh * scale)))
        resized_fg = rgba.resize((new_w, new_h), Image.Resampling.LANCZOS)
        canvas = _make_yaquis_studio_bg(target_w, target_h).convert("RGBA")
        paste_x = (target_w - new_w) // 2
        paste_y = target_h - new_h
        canvas.paste(resized_fg, (paste_x, paste_y), resized_fg.split()[3])
        final_rgb = canvas.convert("RGB")
    else:
        rgb = im.convert("RGB")
        w, h = rgb.size
        target_ratio = target_w / float(target_h)  # 0.8 (4:5)
        cur_ratio = w / float(max(1, h))
        if cur_ratio < target_ratio:
            crop_h = min(h, int(round(w / target_ratio)))
            top = max(0, min(h - crop_h, int((h - crop_h) * 0.14)))
            cropped = rgb.crop((0, top, w, top + crop_h))
        elif cur_ratio > target_ratio:
            crop_w = min(w, int(round(h * target_ratio)))
            left = max(0, (w - crop_w) // 2)
            cropped = rgb.crop((left, 0, left + crop_w, h))
        else:
            cropped = rgb
        final_rgb = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)

    out = io.BytesIO()
    final_rgb.save(out, format="JPEG", quality=quality, optimize=True, progressive=True)
    return out.getvalue()


def download_team_assets() -> None:
    TEAMS_DIR.mkdir(parents=True, exist_ok=True)
    for tid, code in TEAM_PNG_CODES.items():
        png_path = TEAMS_DIR / f"{tid}.png"
        if png_path.exists() and png_path.stat().st_size > 200 and tid != 6484:
            continue
        url = f"https://www.yaquis.com.mx/imagenes/equipos/{code}.png"
        raw = http_get_bytes(url)
        if raw and len(raw) > 200:
            png_path.write_bytes(raw)

    for tid in ALL_TEAM_IDS:
        svg_path = TEAMS_DIR / f"{tid}.svg"
        if svg_path.exists() and svg_path.stat().st_size > 100 and tid != 6484:
            continue
        src_tid = 676 if tid == 6484 else tid
        url = f"https://www.mlbstatic.com/team-logos/{src_tid}.svg"
        raw = http_get_bytes(url)
        if raw and b"<svg" in raw[:500]:
            svg_path.write_bytes(raw)

    for _, (url, fname) in EXTRA_BRAND_URLS.items():
        fpath = TEAMS_DIR / fname
        if fpath.exists() and fpath.stat().st_size > 200:
            continue
        raw = http_get_bytes(url)
        if raw and len(raw) > 200:
            fpath.write_bytes(raw)


def collect_generic_silhouette_hashes() -> set[str]:
    hashes: set[str] = set()
    probe_urls = [
        "https://img.mlbstatic.com/mlb-photos/image/upload/w_320,q_auto:best/v1/people/99999999/headshot/silo/current",
        "https://img.mlbstatic.com/mlb-photos/image/upload/w_320,q_auto:best/v1/people/99999999/headshot/67/current",
    ]
    for url in probe_urls:
        raw = http_get_bytes(url, timeout=10.0)
        if raw and len(raw) > 200:
            hashes.add(hashlib.sha256(raw).hexdigest())
    return hashes


def fetch_one_player(
    pid: int, force_refresh: bool = False, generic_hashes: set[str] | None = None
) -> tuple[int, str | None, str, int]:
    """Tries MLB silo cutout (with alpha), then slot 67, then MiLB, then Wikimedia for Taiki Sekine."""
    out_path = PLAYERS_DIR / f"{pid}.jpg"
    if not force_refresh and out_path.exists() and out_path.stat().st_size > 400:
        return pid, None, "cached", out_path.stat().st_size

    candidates: list[tuple[str, str, bool]] = [
        (
            "silo",
            f"https://img.mlbstatic.com/mlb-photos/image/upload/w_320,q_auto:best/v1/people/{pid}/headshot/silo/current",
            True,
        ),
        (
            "67",
            f"https://img.mlbstatic.com/mlb-photos/image/upload/w_320,q_auto:best/v1/people/{pid}/headshot/67/current",
            False,
        ),
        (
            "milb",
            f"https://img.mlbstatic.com/mlb-photos/image/upload/w_320,q_auto:best/v1/people/{pid}/headshot/milb/current",
            False,
        ),
    ]
    if pid == 692460:
        wiki_url = resolve_taiki_sekine_url()
        if wiki_url:
            candidates.append(("wiki", wiki_url, False))

    ghashes = generic_hashes or set()
    for slot, url, require_alpha in candidates:
        raw = http_get_bytes(url)
        if not raw or len(raw) <= 400:
            continue
        try:
            with Image.open(io.BytesIO(raw)) as probe_im:
                probe_im = ImageOps.exif_transpose(probe_im)
                if require_alpha and not has_true_alpha(probe_im):
                    continue
                if is_generic_silhouette(probe_im, raw, ghashes):
                    continue
            jpg = process_player_portrait(raw, target_w=176, target_h=220, quality=82)
            out_path.write_bytes(jpg)
            return pid, url, slot, len(jpg)
        except Exception:
            continue
    return pid, None, "missing", 0


def download_player_assets(
    player_ids: list[int], force_refresh: bool = False
) -> tuple[dict[int, str], dict[str, int]]:
    PLAYERS_DIR.mkdir(parents=True, exist_ok=True)
    generic_hashes = collect_generic_silhouette_hashes()
    resolved_urls: dict[int, str] = {}
    slot_counts: dict[str, int] = {"silo": 0, "67": 0, "milb": 0, "wiki": 0, "cached": 0, "missing": 0}
    with ThreadPoolExecutor(max_workers=8) as pool:
        futs = {
            pool.submit(fetch_one_player, pid, force_refresh, generic_hashes): pid
            for pid in player_ids
        }
        for fut in as_completed(futs):
            pid, url, slot, _ = fut.result()
            slot_counts[slot] = slot_counts.get(slot, 0) + 1
            if url:
                resolved_urls[pid] = url
    return resolved_urls, slot_counts


def inject_cached_visual_assets(
    payload: dict[str, Any], resolved_urls: dict[int, str] | None = None
) -> dict[str, Any]:
    """Reads cached PNG/SVG team logos and JPG player portraits from web/assets/ and merges
    deduplicated Base64 Data URIs into meta.player_photos. Safe to call after any data rebuild."""
    meta = payload.setdefault("meta", {})
    logos = meta.setdefault("logos", {})

    for key, (_, fname) in EXTRA_BRAND_URLS.items():
        fpath = TEAMS_DIR / fname
        if fpath.exists():
            b64 = base64.b64encode(fpath.read_bytes()).decode("ascii")
            logos[key] = f"data:image/png;base64,{b64}"

    team_logos: dict[str, dict[str, str]] = {}
    for tid in ALL_TEAM_IDS:
        entry: dict[str, str] = {"code": TEAM_PNG_CODES.get(tid, str(tid))}
        png_path = TEAMS_DIR / f"{tid}.png"
        svg_path = TEAMS_DIR / f"{tid}.svg"
        if png_path.exists() and png_path.stat().st_size > 200:
            png_b64 = base64.b64encode(png_path.read_bytes()).decode("ascii")
            entry["data_uri"] = f"data:image/png;base64,{png_b64}"
        elif svg_path.exists() and svg_path.stat().st_size > 100:
            svg_b64 = base64.b64encode(svg_path.read_bytes()).decode("ascii")
            entry["data_uri"] = f"data:image/svg+xml;base64,{svg_b64}"
        if "data_uri" in entry:
            team_logos[str(tid)] = entry
    meta["team_logos"] = team_logos

    # Normalizar franquicia Tucson Baseball Team (6484) -> Mayos de Navojoa
    for sdata in payload.get("seasons", {}).values():
        for tb in sdata.get("team_benchmarks", {}).values():
            for row in tb.get("teams", []):
                if row.get("team_id") in (676, 6484) or "Tucson" in str(row.get("equipo", "")):
                    row["equipo"] = "Mayos de Navojoa"
        for rg in sdata.get("recent_games", []):
            if rg.get("home_team_id") in (676, 6484) or "Tucson" in str(rg.get("home_team_name", "")):
                rg["home_team_name"] = "Mayos de Navojoa"
            if rg.get("away_team_id") in (676, 6484) or "Tucson" in str(rg.get("away_team_name", "")):
                rg["away_team_name"] = "Mayos de Navojoa"

    player_b64_cache: dict[int, str] = {}
    if PLAYERS_DIR.exists():
        for jpg_path in PLAYERS_DIR.glob("*.jpg"):
            if jpg_path.stem.isdigit() and jpg_path.stat().st_size > 200:
                pid = int(jpg_path.stem)
                b64 = base64.b64encode(jpg_path.read_bytes()).decode("ascii")
                player_b64_cache[pid] = f"data:image/jpeg;base64,{b64}"

    # Deduplicate player photos into meta["player_photos"] and omit external URLs (offline/CSP-safe)
    unique_pids: set[int] = set()
    matched_pids: set[int] = set()
    player_photos: dict[str, str] = {}
    for sdata in payload.get("seasons", {}).values():
        for prof in sdata.get("scouting_profiles", []):
            pid = int(prof["player_id"])
            unique_pids.add(pid)
            if pid in player_b64_cache:
                matched_pids.add(pid)
                player_photos[str(pid)] = player_b64_cache[pid]
            prof["headshot_url"] = ""
            prof["headshot_b64"] = None

    meta["player_photos"] = player_photos
    meta["assets_summary"] = {
        "teams_count": len(team_logos),
        "players_total": len(unique_pids),
        "players_with_photo": len(matched_pids),
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Descarga y embebe activos visuales LMP en front_office_payload.json")
    parser.add_argument(
        "--refresh-players",
        action="store_true",
        help="Re-descarga y re-procesa todos los retratos de jugadores en formato 4:5 (176x220).",
    )
    args = parser.parse_args()

    if not PAYLOAD_PATH.exists():
        raise FileNotFoundError(f"No se encontró {PAYLOAD_PATH}")

    payload = json.loads(PAYLOAD_PATH.read_text(encoding="utf-8"))
    unique_pids = sorted(
        {
            int(prof["player_id"])
            for sdata in payload.get("seasons", {}).values()
            for prof in sdata.get("scouting_profiles", [])
        }
    )

    print(f"Descargando logotipos oficiales LMP ({len(ALL_TEAM_IDS)} clubes + emblemas)...")
    download_team_assets()

    print(
        f"Descargando y optimizando fotografías de {len(unique_pids)} jugadores "
        f"(refresh={args.refresh_players})..."
    )
    resolved_urls, slot_counts = download_player_assets(unique_pids, force_refresh=args.refresh_players)
    print(f"Fuentes resueltas: {slot_counts}")

    inject_cached_visual_assets(payload, resolved_urls=resolved_urls)
    out_text = json.dumps(payload, ensure_ascii=False, allow_nan=False, separators=(",", ":"))

    PAYLOAD_PATH.write_text(out_text, encoding="utf-8")
    size_mb = PAYLOAD_PATH.stat().st_size / (1024.0 * 1024.0)
    summary = payload["meta"]["assets_summary"]
    missing = [pid for pid in unique_pids if not (PLAYERS_DIR / f"{pid}.jpg").exists()]
    print(
        f"Activos integrados en {PAYLOAD_PATH} ({size_mb:.2f} MB) | "
        f"Clubes LMP={summary['teams_count']} | "
        f"Fotos reales={summary['players_with_photo']}/{summary['players_total']} | "
        f"Sin foto (placeholder gorra Yaquis CO)={missing}"
    )


if __name__ == "__main__":
    main()
