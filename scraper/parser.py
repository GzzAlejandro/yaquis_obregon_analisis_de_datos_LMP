MLB_HEADSHOT_TMPL = (
    "https://img.mlbstatic.com/mlb-photos/image/upload/"
    "d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/{pid}/headshot/67/current"
)


def parse_players(game_data: dict) -> list[dict]:
    """Extrae el catálogo de jugadores participantes en el juego (con perfil scout)."""
    players = []
    for p in game_data.get("players", {}).values():
        pid = p["id"]
        players.append({
            "player_id": pid,
            "full_name": p.get("fullName", ""),
            "bat_side": p.get("batSide", {}).get("code"),
            "pitch_hand": p.get("pitchHand", {}).get("code"),
            "primary_position": p.get("primaryPosition", {}).get("abbreviation"),
            "birth_country": p.get("birthCountry"),
            "birth_city": p.get("birthCity"),
            "birth_date": p.get("birthDate"),
            "height": p.get("height"),
            "weight": p.get("weight"),
            "mlb_debut_date": p.get("mlbDebutDate"),
            "headshot_url": MLB_HEADSHOT_TMPL.format(pid=pid),
        })
    return players


def parse_game_metadata(feed: dict) -> dict:
    """Extrae clima, marcador final y bandera has_pbp de gameData/liveData."""
    game_data = feed.get("gameData", {})
    live = feed.get("liveData", {})
    weather = game_data.get("weather", {})
    linescore = live.get("linescore", {}).get("teams", {})
    plays = live.get("plays", {}).get("allPlays", [])

    return {
        "temp": str(weather.get("temp")) if weather.get("temp") is not None else None,
        "wind": weather.get("wind"),
        "condition": weather.get("condition"),
        "home_score": linescore.get("home", {}).get("runs"),
        "away_score": linescore.get("away", {}).get("runs"),
        "has_pbp": len(plays) > 0,
    }


def parse_boxscore(game_pk: int, live_data: dict) -> dict[str, list[dict]]:
    """Separa stats de bateo, pitcheo y fildeo sin mezclar columnas ni duplicar jugadores."""
    batting_by_player: dict[int, dict] = {}
    pitching_by_player: dict[int, dict] = {}
    fielding_by_player: dict[int, dict] = {}
    teams = live_data.get("boxscore", {}).get("teams", {})

    for side in ("away", "home"):
        team_block = teams.get(side, {})
        team_id = team_block.get("team", {}).get("id")
        if not team_id:
            continue

        for p_obj in team_block.get("players", {}).values():
            player_id = p_obj.get("person", {}).get("id")
            if not player_id:
                continue
            stats = p_obj.get("stats", {})
            pos = p_obj.get("position", {}).get("abbreviation")

            if bat := stats.get("batting"):
                pa = bat.get("plateAppearances", 0)
                gp = bat.get("gamesPlayed", 0)
                if gp > 0 or pa > 0 or bat.get("runs", 0) > 0 or bat.get("stolenBases", 0) > 0:
                    row = {
                        "game_pk": game_pk, "team_id": team_id, "player_id": player_id,
                        "position": pos,
                        "is_substitute": bool(p_obj.get("gameStatus", {}).get("isSubstitute", False)),
                        "plate_appearances": pa,
                        "at_bats": bat.get("atBats", 0), "runs": bat.get("runs", 0),
                        "hits": bat.get("hits", 0), "doubles": bat.get("doubles", 0),
                        "triples": bat.get("triples", 0), "home_runs": bat.get("homeRuns", 0),
                        "rbi": bat.get("rbi", 0), "total_bases": bat.get("totalBases", 0),
                        "walks": bat.get("baseOnBalls", 0),
                        "intentional_walks": bat.get("intentionalWalks", 0),
                        "hit_by_pitch": bat.get("hitByPitch", 0),
                        "strikeouts": bat.get("strikeOuts", 0),
                        "stolen_bases": bat.get("stolenBases", 0),
                        "caught_stealing": bat.get("caughtStealing", 0),
                        "sac_bunts": bat.get("sacBunts", 0), "sac_flies": bat.get("sacFlies", 0),
                        "gidp": bat.get("groundIntoDoublePlay", 0),
                        "left_on_base": bat.get("leftOnBase", 0),
                        "ground_outs": bat.get("groundOuts", 0), "air_outs": bat.get("airOuts", 0),
                        "fly_outs": bat.get("flyOuts", 0), "line_outs": bat.get("lineOuts", 0),
                        "pop_outs": bat.get("popOuts", 0),
                    }
                    prev = batting_by_player.get(player_id)
                    if prev is None or row["plate_appearances"] >= prev["plate_appearances"]:
                        batting_by_player[player_id] = row

            if pit := stats.get("pitching"):
                outs = pit.get("outs", 0)
                bf = pit.get("battersFaced", 0)
                gp = pit.get("gamesPlayed", 0) or pit.get("gamesPitched", 0)
                if gp > 0 or outs > 0 or bf > 0:
                    row = {
                        "game_pk": game_pk, "team_id": team_id, "player_id": player_id,
                        "games_started": pit.get("gamesStarted", 0),
                        "games_finished": pit.get("gamesFinished", 0),
                        "innings_pitched": pit.get("inningsPitched"),
                        "outs": outs,
                        "batters_faced": bf,
                        "pitches_thrown": pit.get("pitchesThrown") or pit.get("numberOfPitches", 0),
                        "balls": pit.get("balls", 0), "strikes": pit.get("strikes", 0),
                        "hits": pit.get("hits", 0), "runs": pit.get("runs", 0),
                        "earned_runs": pit.get("earnedRuns", 0), "home_runs": pit.get("homeRuns", 0),
                        "walks": pit.get("baseOnBalls", 0),
                        "intentional_walks": pit.get("intentionalWalks", 0),
                        "strikeouts": pit.get("strikeOuts", 0),
                        "hit_batsmen": pit.get("hitBatsmen", 0),
                        "wild_pitches": pit.get("wildPitches", 0), "balks": pit.get("balks", 0),
                        "wins": pit.get("wins", 0), "losses": pit.get("losses", 0),
                        "holds": pit.get("holds", 0), "saves": pit.get("saves", 0),
                        "blown_saves": pit.get("blownSaves", 0),
                        "inherited_runners": pit.get("inheritedRunners", 0),
                        "inherited_runners_scored": pit.get("inheritedRunnersScored", 0),
                    }
                    prev = pitching_by_player.get(player_id)
                    if prev is None or (row["outs"], row["batters_faced"]) >= (prev["outs"], prev["batters_faced"]):
                        pitching_by_player[player_id] = row

            if fld := stats.get("fielding"):
                chances = fld.get("chances", 0)
                gs = fld.get("gamesStarted", 0)
                pb = fld.get("passedBall", 0)
                if pos is not None or chances > 0 or gs > 0 or pb > 0:
                    row = {
                        "game_pk": game_pk, "team_id": team_id, "player_id": player_id,
                        "position": pos,
                        "games_started": gs,
                        "put_outs": fld.get("putOuts", 0), "assists": fld.get("assists", 0),
                        "errors": fld.get("errors", 0), "chances": chances,
                        "passed_balls": pb,
                        "stolen_bases_allowed": fld.get("stolenBases", 0),
                        "caught_stealing": fld.get("caughtStealing", 0),
                    }
                    prev = fielding_by_player.get(player_id)
                    if prev is None or (row["chances"], row["games_started"], row["position"] is not None) > (
                        prev["chances"], prev["games_started"], prev["position"] is not None
                    ):
                        fielding_by_player[player_id] = row

    return {
        "batting": list(batting_by_player.values()),
        "pitching": list(pitching_by_player.values()),
        "fielding": list(fielding_by_player.values()),
    }


def parse_plays_and_pitches(
    game_pk: int, home_team_id: int, away_team_id: int, live_data: dict
) -> list[dict]:
    """Extrae cada turno al bat (con splits, is_risp pre-turno y hitData) y sus lanzamientos."""
    parsed_plays = []
    current_half_key = None
    prev_men_on_base = "Empty"

    for play in live_data.get("plays", {}).get("allPlays", []):
        about = play.get("about", {})
        matchup = play.get("matchup", {})
        result = play.get("result", {})
        inning = about.get("inning")
        half = about.get("halfInning", "top")

        half_key = (inning, half)
        if half_key != current_half_key:
            current_half_key = half_key
            prev_men_on_base = "Empty"

        # En statsapi.mlb.com, matchup.splits.menOnBase refleja el estado POST-turno;
        # el estado PRE-turno real proviene del menOnBase del turno anterior en el mismo medio inning.
        is_risp = prev_men_on_base in ("RISP", "Loaded")
        prev_men_on_base = matchup.get("splits", {}).get("menOnBase", "Empty")

        batter_id = matchup.get("batter", {}).get("id")
        pitcher_id = matchup.get("pitcher", {}).get("id")
        if not batter_id or not pitcher_id:
            continue

        batting_team_id = away_team_id if half == "top" else home_team_id
        pitching_team_id = home_team_id if half == "top" else away_team_id

        events = play.get("playEvents", [])
        hit_data = next((e["hitData"] for e in reversed(events) if "hitData" in e), {})
        hit_coords = hit_data.get("coordinates", {})

        pitches = []
        for ev in events:
            if not ev.get("isPitch"):
                continue
            details = ev.get("details", {})
            pdata = ev.get("pitchData", {})
            pcoords = pdata.get("coordinates", {})
            count = ev.get("count", {})
            pitches.append({
                "pitch_number": ev.get("pitchNumber"),
                "call_code": details.get("call", {}).get("code"),
                "call_description": details.get("call", {}).get("description"),
                "is_in_play": details.get("isInPlay"),
                "is_strike": details.get("isStrike"),
                "is_ball": details.get("isBall"),
                "balls_after": count.get("balls"),
                "strikes_after": count.get("strikes"),
                "pitch_x": pcoords.get("x"),
                "pitch_y": pcoords.get("y"),
                "sz_top": pdata.get("strikeZoneTop"),
                "sz_bot": pdata.get("strikeZoneBottom"),
            })

        parsed_plays.append({
            "pa": {
                "game_pk": game_pk,
                "at_bat_index": play.get("atBatIndex"),
                "inning": about.get("inning"),
                "half_inning": half,
                "batting_team_id": batting_team_id,
                "pitching_team_id": pitching_team_id,
                "batter_id": batter_id,
                "pitcher_id": pitcher_id,
                "bat_side": matchup.get("batSide", {}).get("code"),
                "pitch_hand": matchup.get("pitchHand", {}).get("code"),
                "event": result.get("event"),
                "event_type": result.get("eventType"),
                "is_out": result.get("isOut"),
                "rbi": result.get("rbi", 0),
                "is_risp": is_risp,
                "home_score_after": result.get("homeScore"),
                "away_score_after": result.get("awayScore"),
                "hit_coord_x": hit_coords.get("coordX"),
                "hit_coord_y": hit_coords.get("coordY"),
                "hit_hardness": hit_data.get("hardness"),
                "hit_location": hit_data.get("location"),
                "hit_trajectory": hit_data.get("trajectory"),
            },
            "pitches": pitches,
        })
    return parsed_plays
