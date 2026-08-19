from pydantic import BaseModel, Field

from app.models import MatchStatus, Player, PointOutcome, ShotType


class YouTubeIngestRequest(BaseModel):
    url: str


class MatchOut(BaseModel):
    id: int
    source_type: str
    source_reference: str
    status: MatchStatus
    error_message: str | None = None

    model_config = {"from_attributes": True}


class Corner(BaseModel):
    x: float
    y: float


class CalibrationRequest(BaseModel):
    # Exactly 4 corners, clicked in order: near-left, near-right, far-right, far-left.
    corners: list[Corner] = Field(min_length=4, max_length=4)
    frame_width: int
    frame_height: int


class CalibrationOut(BaseModel):
    corners: list[Corner]
    frame_width: int
    frame_height: int

    model_config = {"from_attributes": True}


class ShotOut(BaseModel):
    shot_index: int
    hitter: Player
    shot_type: ShotType
    contact_x: float
    contact_y: float
    contact_time: float
    bounce_x: float
    bounce_y: float
    bounce_time: float
    speed: float

    model_config = {"from_attributes": True}


class PointOut(BaseModel):
    index: int
    server: Player
    winner: Player
    outcome: PointOutcome
    shots: list[ShotOut]

    model_config = {"from_attributes": True}


class PlayerStats(BaseModel):
    points_won: int
    winners: int
    errors: int
    avg_serve_speed: float | None
    avg_groundstroke_speed: float | None
    # "Player" heatmap: where this player made contact (their court positioning).
    contact_locations: list[tuple[float, float]]
    # "Shots" heatmap: where this player's shots landed (first bounce).
    bounce_locations: list[tuple[float, float]]


class StatsOut(BaseModel):
    player1: PlayerStats
    player2: PlayerStats
    total_points: int
