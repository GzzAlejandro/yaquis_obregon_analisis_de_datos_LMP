import time
from datetime import date
import requests


PLAYOFF_GAME_TYPES = {"F", "D", "L", "W"}


class MLBStatsClient:
    """Conector modular para statsapi.mlb.com (patrón data-scraper-agent)."""

    def __init__(self, config: dict):
        src = config["source"]
        scr = config["scraping"]
        self.api_root = src["api_root"].rstrip("/")
        self.sport_id = src["sport_id"]
        self.league_id = src["league_id"]
        self.allowed_game_types = set(src["allowed_game_types"])
        self.rate_limit = scr["rate_limit_seconds"]
        self.timeout = scr["timeout_seconds"]

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": scr["user_agent"]})
        self._last_call = 0.0

    def _get(self, path: str, params: dict | None = None, max_retries: int = 3) -> dict:
        url = f"{self.api_root}/{path.lstrip('/')}"
        for attempt in range(max_retries):
            elapsed = time.time() - self._last_call
            if elapsed < self.rate_limit:
                time.sleep(self.rate_limit - elapsed)
            try:
                resp = self.session.get(url, params=params, timeout=self.timeout)
                self._last_call = time.time()
                if resp.status_code in (429, 500, 502, 503, 504) and attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException:
                self._last_call = time.time()
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
        return {}

    def fetch_teams(self, season: int) -> list[dict]:
        """Obtiene el catálogo de equipos de la LMP para una temporada."""
        data = self._get(
            "/api/v1/teams",
            params={"sportId": self.sport_id, "leagueIds": self.league_id, "season": season},
        )
        return [
            {
                "team_id": t["id"],
                "name": t.get("name", ""),
                "abbreviation": t.get("abbreviation", ""),
                "team_code": t.get("teamCode", ""),
                "venue_id": t.get("venue", {}).get("id"),
                "venue_name": t.get("venue", {}).get("name", ""),
            }
            for t in data.get("teams", [])
        ]

    def fetch_schedule(self, season: int) -> list[dict]:
        """Obtiene el calendario oficial (excluyendo pretemporada); usa fallback si leagueId viene vacío."""
        data = self._get(
            "/api/v1/schedule",
            params={"sportId": self.sport_id, "leagueId": self.league_id, "season": season},
        )
        dates = data.get("dates", [])

        if not dates:
            lmp_ids = {t["team_id"] for t in self.fetch_teams(season)} or {
                673, 674, 675, 676, 677, 678, 679, 680
            }
            win_data = self._get(
                "/api/v1/schedule",
                params={
                    "sportId": self.sport_id,
                    "startDate": f"{season}-10-01",
                    "endDate": f"{season + 1}-02-15",
                },
            )
            dates = [
                {
                    "games": [
                        g for g in day.get("games", [])
                        if g["teams"]["home"]["team"]["id"] in lmp_ids
                        and g["teams"]["away"]["team"]["id"] in lmp_ids
                    ]
                }
                for day in win_data.get("dates", [])
            ]

        games = []
        for day in dates:
            for g in day.get("games", []):
                game_type = g.get("gameType", "R")
                if game_type not in self.allowed_game_types:
                    continue

                status = g.get("status", {})
                abstract_state = status.get("abstractGameState", "")
                coded_state = status.get("codedGameState", "")
                is_completed = abstract_state == "Final" or coded_state in ("F", "O")
                game_stage = "PLAYOFFS" if game_type in PLAYOFF_GAME_TYPES else "REGULAR"

                games.append({
                    "game_pk": g["gamePk"],
                    "season": season,
                    "game_type": game_type,
                    "game_stage": game_stage,
                    "game_date": date.fromisoformat(g["officialDate"]),
                    "status_code": coded_state,
                    "status_detail": status.get("detailedState", "Final") if is_completed else "POR_JUGAR",
                    "is_completed": is_completed,
                    "home_team_id": g["teams"]["home"]["team"]["id"],
                    "away_team_id": g["teams"]["away"]["team"]["id"],
                    "home_score": g["teams"]["home"].get("score") if is_completed else None,
                    "away_score": g["teams"]["away"].get("score") if is_completed else None,
                    "venue_id": g.get("venue", {}).get("id"),
                })
        return games

    def fetch_game_feed(self, game_pk: int) -> dict:
        """Descarga el feed completo v1.1 (boxscore + play-by-play) de un partido."""
        return self._get(f"/api/v1.1/game/{game_pk}/feed/live")
