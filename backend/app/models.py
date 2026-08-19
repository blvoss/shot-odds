import datetime
import enum

from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class MatchStatus(str, enum.Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    READY_FOR_CALIBRATION = "ready_for_calibration"
    CALIBRATED = "calibrated"
    PROCESSING = "processing"
    DONE = "done"
    ERROR = "error"


class Player(str, enum.Enum):
    PLAYER_1 = "player1"
    PLAYER_2 = "player2"


class PointOutcome(str, enum.Enum):
    WINNER = "winner"
    ERROR = "error"


class ShotType(str, enum.Enum):
    SERVE = "serve"
    GROUNDSTROKE = "groundstroke"
    OTHER = "other"


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_type: Mapped[str] = mapped_column(String, nullable=False)  # "upload" | "youtube"
    source_reference: Mapped[str] = mapped_column(String, nullable=False)  # filename or URL
    video_path: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[MatchStatus] = mapped_column(
        Enum(MatchStatus), default=MatchStatus.PENDING, nullable=False
    )
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )

    calibration: Mapped["CourtCalibration | None"] = relationship(
        back_populates="match", uselist=False, cascade="all, delete-orphan"
    )
    points: Mapped[list["Point"]] = relationship(
        back_populates="match", cascade="all, delete-orphan", order_by="Point.index"
    )


class CourtCalibration(Base):
    __tablename__ = "court_calibrations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), unique=True)

    # Pixel coordinates of the 4 singles-court corners, clicked in order:
    # near-left, near-right, far-right, far-left (baseline corners).
    corners: Mapped[list] = mapped_column(JSON, nullable=False)
    frame_width: Mapped[int] = mapped_column(Integer, nullable=False)
    frame_height: Mapped[int] = mapped_column(Integer, nullable=False)

    match: Mapped["Match"] = relationship(back_populates="calibration")


class Point(Base):
    __tablename__ = "points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"))
    index: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-based order within match
    server: Mapped[Player] = mapped_column(Enum(Player), nullable=False)
    winner: Mapped[Player] = mapped_column(Enum(Player), nullable=False)
    outcome: Mapped[PointOutcome] = mapped_column(Enum(PointOutcome), nullable=False)

    match: Mapped["Match"] = relationship(back_populates="points")
    shots: Mapped[list["Shot"]] = relationship(
        back_populates="point", cascade="all, delete-orphan", order_by="Shot.shot_index"
    )


class Shot(Base):
    __tablename__ = "shots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    point_id: Mapped[int] = mapped_column(ForeignKey("points.id"))
    shot_index: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-based order within point
    hitter: Mapped[Player] = mapped_column(Enum(Player), nullable=False)
    shot_type: Mapped[ShotType] = mapped_column(Enum(ShotType), nullable=False)

    # Coordinates are in real-world court meters (x: 0-8.23 singles width, y: 0-23.77 length),
    # mapped from pixels via the match's calibration homography, not raw pixel coordinates.
    contact_x: Mapped[float] = mapped_column(Float, nullable=False)
    contact_y: Mapped[float] = mapped_column(Float, nullable=False)
    contact_time: Mapped[float] = mapped_column(Float, nullable=False)  # seconds into video

    bounce_x: Mapped[float] = mapped_column(Float, nullable=False)
    bounce_y: Mapped[float] = mapped_column(Float, nullable=False)
    bounce_time: Mapped[float] = mapped_column(Float, nullable=False)  # seconds into video

    speed: Mapped[float] = mapped_column(Float, nullable=False)  # meters per second

    point: Mapped["Point"] = relationship(back_populates="shots")
