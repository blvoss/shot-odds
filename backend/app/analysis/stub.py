"""Fake analysis pipeline for Phase 1.

Generates a plausible-looking sequence of points and shots for a calibrated
match without running any real computer vision. This lets the rest of the
app (API, dashboard, filters) be built and exercised end-to-end before the
real TrackNet/YOLO pipeline (Phase 2) replaces this module.
"""

import random

from app.court import SINGLES_COURT_LENGTH, SINGLES_COURT_WIDTH
from app.models import Player, PointOutcome, ShotType

SERVE_SPEED_RANGE = (35.0, 55.0)  # m/s, ~126-198 km/h
GROUNDSTROKE_SPEED_RANGE = (15.0, 35.0)  # m/s, ~54-126 km/h

_OTHER_PLAYER = {
    Player.PLAYER_1: Player.PLAYER_2,
    Player.PLAYER_2: Player.PLAYER_1,
}


def _random_court_point(rng: random.Random) -> tuple[float, float]:
    return (
        rng.uniform(0.0, SINGLES_COURT_WIDTH),
        rng.uniform(0.0, SINGLES_COURT_LENGTH),
    )


def _random_shot(
    rng: random.Random,
    hitter: Player,
    shot_type: ShotType,
    t: float,
) -> dict:
    contact_x, contact_y = _random_court_point(rng)
    bounce_x, bounce_y = _random_court_point(rng)

    speed_range = SERVE_SPEED_RANGE if shot_type == ShotType.SERVE else GROUNDSTROKE_SPEED_RANGE
    speed = rng.uniform(*speed_range)

    distance = ((bounce_x - contact_x) ** 2 + (bounce_y - contact_y) ** 2) ** 0.5
    flight_time = max(distance / speed, 0.05)

    return {
        "hitter": hitter,
        "shot_type": shot_type,
        "contact_x": contact_x,
        "contact_y": contact_y,
        "contact_time": t,
        "bounce_x": bounce_x,
        "bounce_y": bounce_y,
        "bounce_time": t + flight_time,
        "speed": speed,
    }, t + flight_time + rng.uniform(0.3, 1.0)  # gap before the next shot


def generate_fake_points(num_points: int | None = None, seed: int | None = None) -> list[dict]:
    """Returns a list of point dicts: {index, server, winner, outcome, shots: [...]}."""
    rng = random.Random(seed)
    num_points = num_points or rng.randint(12, 24)

    points: list[dict] = []
    server = rng.choice([Player.PLAYER_1, Player.PLAYER_2])
    t = 0.0
    points_since_server_change = 0

    for point_index in range(1, num_points + 1):
        num_shots = rng.randint(1, 8)
        hitter = server
        shots: list[dict] = []

        for shot_index in range(1, num_shots + 1):
            shot_type = ShotType.SERVE if shot_index == 1 else ShotType.GROUNDSTROKE
            shot, t = _random_shot(rng, hitter, shot_type, t)
            shot["shot_index"] = shot_index
            shots.append(shot)
            hitter = _OTHER_PLAYER[hitter]

        last_shot = shots[-1]
        outcome = rng.choice([PointOutcome.WINNER, PointOutcome.ERROR])
        if outcome == PointOutcome.WINNER:
            winner = last_shot["hitter"]
        else:
            winner = _OTHER_PLAYER[last_shot["hitter"]]

        points.append(
            {
                "index": point_index,
                "server": server,
                "winner": winner,
                "outcome": outcome,
                "shots": shots,
            }
        )

        t += rng.uniform(5.0, 15.0)  # gap between points

        points_since_server_change += 1
        if points_since_server_change >= rng.randint(3, 6):
            server = _OTHER_PLAYER[server]
            points_since_server_change = 0

    return points
