from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
    event,
)
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Team(Base):
    __tablename__ = "teams"

    team_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    abbreviation = Column(String(10))
    team_code = Column(String(10))
    venue_id = Column(Integer)
    venue_name = Column(String)


class Game(Base):
    __tablename__ = "games"

    game_pk = Column(Integer, primary_key=True)
    season = Column(Integer, nullable=False, index=True)  # ej. 2025 = temp. 2025-26
    game_type = Column(String(5), nullable=False, index=True)  # R, D, L, W
    game_stage = Column(String(20), nullable=False, index=True)  # REGULAR / PLAYOFFS
    game_date = Column(Date, nullable=False, index=True)
    status_code = Column(String(10))
    status_detail = Column(String(30), default="POR_JUGAR", nullable=False, index=True)
    is_completed = Column(Boolean, default=False, nullable=False, index=True)
    home_team_id = Column(Integer, ForeignKey("teams.team_id"), nullable=False, index=True)
    away_team_id = Column(Integer, ForeignKey("teams.team_id"), nullable=False, index=True)
    home_score = Column(Integer)
    away_score = Column(Integer)
    venue_id = Column(Integer)
    temp = Column(String(20))
    wind = Column(String(50))
    condition = Column(String(50))
    has_pbp = Column(Boolean, default=False, nullable=False)


class Player(Base):
    __tablename__ = "players"

    player_id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False, index=True)
    bat_side = Column(String(5))    # L, R, S
    pitch_hand = Column(String(5))  # L, R
    primary_position = Column(String(10))
    birth_country = Column(String(60))
    birth_city = Column(String(80))
    birth_date = Column(String(20))
    height = Column(String(20))
    weight = Column(Integer)
    mlb_debut_date = Column(String(20))
    headshot_url = Column(String(255))


class BattingGameStat(Base):
    __tablename__ = "batting_game_stats"
    __table_args__ = (UniqueConstraint("game_pk", "player_id", name="uq_bat_game_player"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_pk = Column(Integer, ForeignKey("games.game_pk"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.team_id"), nullable=False, index=True)
    player_id = Column(Integer, ForeignKey("players.player_id"), nullable=False, index=True)

    position = Column(String(10), index=True)
    is_substitute = Column(Boolean, default=False, nullable=False)
    plate_appearances = Column(Integer, default=0)
    at_bats = Column(Integer, default=0)
    runs = Column(Integer, default=0)
    hits = Column(Integer, default=0)
    doubles = Column(Integer, default=0)
    triples = Column(Integer, default=0)
    home_runs = Column(Integer, default=0)
    rbi = Column(Integer, default=0)
    total_bases = Column(Integer, default=0)
    walks = Column(Integer, default=0)
    intentional_walks = Column(Integer, default=0)
    hit_by_pitch = Column(Integer, default=0)
    strikeouts = Column(Integer, default=0)
    stolen_bases = Column(Integer, default=0)
    caught_stealing = Column(Integer, default=0)
    sac_bunts = Column(Integer, default=0)
    sac_flies = Column(Integer, default=0)
    gidp = Column(Integer, default=0)
    left_on_base = Column(Integer, default=0)
    ground_outs = Column(Integer, default=0)
    air_outs = Column(Integer, default=0)
    fly_outs = Column(Integer, default=0)
    line_outs = Column(Integer, default=0)
    pop_outs = Column(Integer, default=0)


class PitchingGameStat(Base):
    __tablename__ = "pitching_game_stats"
    __table_args__ = (UniqueConstraint("game_pk", "player_id", name="uq_pit_game_player"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_pk = Column(Integer, ForeignKey("games.game_pk"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.team_id"), nullable=False, index=True)
    player_id = Column(Integer, ForeignKey("players.player_id"), nullable=False, index=True)

    games_started = Column(Integer, default=0)
    games_finished = Column(Integer, default=0)
    innings_pitched = Column(String(10))
    outs = Column(Integer, default=0)
    batters_faced = Column(Integer, default=0)
    pitches_thrown = Column(Integer, default=0)
    balls = Column(Integer, default=0)
    strikes = Column(Integer, default=0)
    hits = Column(Integer, default=0)
    runs = Column(Integer, default=0)
    earned_runs = Column(Integer, default=0)
    home_runs = Column(Integer, default=0)
    walks = Column(Integer, default=0)
    intentional_walks = Column(Integer, default=0)
    strikeouts = Column(Integer, default=0)
    hit_batsmen = Column(Integer, default=0)
    wild_pitches = Column(Integer, default=0)
    balks = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    holds = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    blown_saves = Column(Integer, default=0)
    inherited_runners = Column(Integer, default=0)
    inherited_runners_scored = Column(Integer, default=0)


class FieldingGameStat(Base):
    __tablename__ = "fielding_game_stats"
    __table_args__ = (UniqueConstraint("game_pk", "player_id", name="uq_fld_game_player"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_pk = Column(Integer, ForeignKey("games.game_pk"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.team_id"), nullable=False, index=True)
    player_id = Column(Integer, ForeignKey("players.player_id"), nullable=False, index=True)

    position = Column(String(10), index=True)
    games_started = Column(Integer, default=0)
    put_outs = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    errors = Column(Integer, default=0)
    chances = Column(Integer, default=0)
    passed_balls = Column(Integer, default=0)
    stolen_bases_allowed = Column(Integer, default=0)
    caught_stealing = Column(Integer, default=0)


class PlateAppearance(Base):
    __tablename__ = "plate_appearances"
    __table_args__ = (UniqueConstraint("game_pk", "at_bat_index", name="uq_pa_game_idx"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_pk = Column(Integer, ForeignKey("games.game_pk"), nullable=False, index=True)
    at_bat_index = Column(Integer, nullable=False)
    inning = Column(Integer, nullable=False)
    half_inning = Column(String(10), nullable=False)  # top / bottom
    batting_team_id = Column(Integer, ForeignKey("teams.team_id"), nullable=False, index=True)
    pitching_team_id = Column(Integer, ForeignKey("teams.team_id"), nullable=False, index=True)
    batter_id = Column(Integer, ForeignKey("players.player_id"), nullable=False, index=True)
    pitcher_id = Column(Integer, ForeignKey("players.player_id"), nullable=False, index=True)
    bat_side = Column(String(5))
    pitch_hand = Column(String(5))

    event = Column(String(50))
    event_type = Column(String(50), index=True)
    is_out = Column(Boolean)
    rbi = Column(Integer, default=0)
    is_risp = Column(Boolean, default=False)
    home_score_after = Column(Integer)
    away_score_after = Column(Integer)

    # Coordenadas 2D del batazo (Spray Chart)
    hit_coord_x = Column(Float)
    hit_coord_y = Column(Float)
    hit_hardness = Column(String(20))
    hit_location = Column(String(10), index=True)
    hit_trajectory = Column(String(30))


class Pitch(Base):
    __tablename__ = "pitches"
    __table_args__ = (UniqueConstraint("pa_id", "pitch_number", name="uq_pitch_pa_num"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    pa_id = Column(Integer, ForeignKey("plate_appearances.id"), nullable=False, index=True)
    pitch_number = Column(Integer, nullable=False)
    call_code = Column(String(10), index=True)
    call_description = Column(String(50))
    is_in_play = Column(Boolean)
    is_strike = Column(Boolean)
    is_ball = Column(Boolean)
    balls_after = Column(Integer)
    strikes_after = Column(Integer)

    # Coordenadas 2D en zona de strike (anotador oficial)
    pitch_x = Column(Float)
    pitch_y = Column(Float)
    sz_top = Column(Float)
    sz_bot = Column(Float)


def init_db(sqlite_path: str):
    engine = create_engine(
        f"sqlite:///{sqlite_path}",
        connect_args={"timeout": 30},
        future=True,
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_wal(dbapi_conn, _conn_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.close()

    Base.metadata.create_all(engine)
    return engine, sessionmaker(bind=engine, future=True)
