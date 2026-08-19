import os
import time

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import video
from app.analysis.stub import generate_fake_points
from app.db import Base, engine, get_db
from app.models import CourtCalibration, Match, MatchStatus, Player, Point, Shot
from app.schemas import (
    CalibrationOut,
    CalibrationRequest,
    MatchOut,
    PointOut,
    StatsOut,
    YouTubeIngestRequest,
)
from app.stats import compute_player_stats

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tennis Match Analysis API")

cors_origins = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_match_or_404(db: Session, match_id: int) -> Match:
    match = db.get(Match, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return match


def _prepare_calibration_frame(match_id: int) -> None:
    """Runs as a background task, so it opens its own DB session rather than
    reusing a request-scoped one, which FastAPI may have already closed."""
    from app.db import SessionLocal

    db = SessionLocal()
    try:
        match = db.get(Match, match_id)
        try:
            video.extract_first_frame(match.video_path, match_id)
            match.status = MatchStatus.READY_FOR_CALIBRATION
        except Exception as exc:  # noqa: BLE001 - surface any extraction failure on the match
            match.status = MatchStatus.ERROR
            match.error_message = str(exc)
        db.commit()
    finally:
        db.close()


def _download_youtube_task(match_id: int, url: str) -> None:
    from app.db import SessionLocal

    db = SessionLocal()
    try:
        match = db.get(Match, match_id)
        try:
            video_path = video.download_youtube_video(url)
            match.video_path = video_path
            db.commit()
        except Exception as exc:  # noqa: BLE001
            match.status = MatchStatus.ERROR
            match.error_message = str(exc)
            db.commit()
            return
    finally:
        db.close()

    _prepare_calibration_frame(match_id)


def _run_fake_analysis_task(match_id: int) -> None:
    from app.db import SessionLocal

    db = SessionLocal()
    try:
        time.sleep(3)  # simulate processing time
        match = db.get(Match, match_id)
        fake_points = generate_fake_points()
        for point_data in fake_points:
            point = Point(
                match_id=match_id,
                index=point_data["index"],
                server=point_data["server"],
                winner=point_data["winner"],
                outcome=point_data["outcome"],
            )
            db.add(point)
            db.flush()  # assign point.id
            for shot_data in point_data["shots"]:
                db.add(
                    Shot(
                        point_id=point.id,
                        shot_index=shot_data["shot_index"],
                        hitter=shot_data["hitter"],
                        shot_type=shot_data["shot_type"],
                        contact_x=shot_data["contact_x"],
                        contact_y=shot_data["contact_y"],
                        contact_time=shot_data["contact_time"],
                        bounce_x=shot_data["bounce_x"],
                        bounce_y=shot_data["bounce_y"],
                        bounce_time=shot_data["bounce_time"],
                        speed=shot_data["speed"],
                    )
                )
        match.status = MatchStatus.DONE
        db.commit()
    except Exception as exc:  # noqa: BLE001
        match = db.get(Match, match_id)
        match.status = MatchStatus.ERROR
        match.error_message = str(exc)
        db.commit()
    finally:
        db.close()


@app.post("/matches/upload", response_model=MatchOut)
def upload_match(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    db: Session = Depends(get_db),
):
    content = file.file.read()
    video_path = video.save_uploaded_video(file.filename, content)

    match = Match(
        source_type="upload",
        source_reference=file.filename,
        video_path=video_path,
        status=MatchStatus.PENDING,
    )
    db.add(match)
    db.commit()
    db.refresh(match)

    background_tasks.add_task(_prepare_calibration_frame, match.id)
    return match


@app.post("/matches/from-youtube", response_model=MatchOut)
def ingest_youtube_match(
    request: YouTubeIngestRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    match = Match(
        source_type="youtube",
        source_reference=request.url,
        status=MatchStatus.DOWNLOADING,
    )
    db.add(match)
    db.commit()
    db.refresh(match)

    background_tasks.add_task(_download_youtube_task, match.id, request.url)
    return match


@app.get("/matches/{match_id}", response_model=MatchOut)
def get_match(match_id: int, db: Session = Depends(get_db)):
    return _get_match_or_404(db, match_id)


@app.get("/matches/{match_id}/status", response_model=MatchOut)
def get_match_status(match_id: int, db: Session = Depends(get_db)):
    return _get_match_or_404(db, match_id)


@app.get("/matches/{match_id}/calibration-frame")
def get_calibration_frame(match_id: int, db: Session = Depends(get_db)):
    _get_match_or_404(db, match_id)
    frame_path = os.path.join(
        os.environ.get("FRAME_STORAGE_DIR", "./storage/frames"),
        f"match_{match_id}_first_frame.jpg",
    )
    if not os.path.exists(frame_path):
        raise HTTPException(status_code=404, detail="Calibration frame not available yet")
    return FileResponse(frame_path, media_type="image/jpeg")


@app.post("/matches/{match_id}/calibration", response_model=CalibrationOut)
def set_calibration(
    match_id: int,
    request: CalibrationRequest,
    db: Session = Depends(get_db),
):
    match = _get_match_or_404(db, match_id)

    existing = db.query(CourtCalibration).filter_by(match_id=match_id).first()
    if existing:
        db.delete(existing)
        db.flush()

    calibration = CourtCalibration(
        match_id=match_id,
        corners=[c.model_dump() for c in request.corners],
        frame_width=request.frame_width,
        frame_height=request.frame_height,
    )
    db.add(calibration)
    match.status = MatchStatus.CALIBRATED
    db.commit()
    db.refresh(calibration)
    return calibration


@app.post("/matches/{match_id}/process", response_model=MatchOut)
def process_match(
    match_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    match = _get_match_or_404(db, match_id)
    if match.status != MatchStatus.CALIBRATED:
        raise HTTPException(
            status_code=400,
            detail=f"Match must be calibrated before processing (current status: {match.status})",
        )

    match.status = MatchStatus.PROCESSING
    db.commit()
    db.refresh(match)

    background_tasks.add_task(_run_fake_analysis_task, match_id)
    return match


def _filtered_points_query(
    db: Session,
    match_id: int,
    server: Player | None,
    winner: Player | None,
    start: int | None,
    end: int | None,
):
    query = db.query(Point).filter(Point.match_id == match_id)
    if server is not None:
        query = query.filter(Point.server == server)
    if winner is not None:
        query = query.filter(Point.winner == winner)
    if start is not None:
        query = query.filter(Point.index >= start)
    if end is not None:
        query = query.filter(Point.index <= end)
    return query.order_by(Point.index)


@app.get("/matches/{match_id}/points", response_model=list[PointOut])
def list_points(
    match_id: int,
    server: Player | None = None,
    winner: Player | None = None,
    start: int | None = None,
    end: int | None = None,
    db: Session = Depends(get_db),
):
    _get_match_or_404(db, match_id)
    return _filtered_points_query(db, match_id, server, winner, start, end).all()


@app.get("/matches/{match_id}/stats", response_model=StatsOut)
def get_stats(
    match_id: int,
    server: Player | None = None,
    winner: Player | None = None,
    start: int | None = None,
    end: int | None = None,
    db: Session = Depends(get_db),
):
    _get_match_or_404(db, match_id)
    points = _filtered_points_query(db, match_id, server, winner, start, end).all()

    return StatsOut(
        player1=compute_player_stats(points, Player.PLAYER_1),
        player2=compute_player_stats(points, Player.PLAYER_2),
        total_points=len(points),
    )
