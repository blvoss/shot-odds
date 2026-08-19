from app.models import Player, PointOutcome, ShotType


def _avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def compute_player_stats(points: list, player: Player) -> dict:
    points_won = 0
    winners = 0
    errors = 0
    serve_speeds: list[float] = []
    groundstroke_speeds: list[float] = []
    contact_locations: list[tuple[float, float]] = []
    bounce_locations: list[tuple[float, float]] = []

    for point in points:
        if point.winner == player:
            points_won += 1

        last_shot = point.shots[-1] if point.shots else None
        if last_shot and last_shot.hitter == player:
            if point.outcome == PointOutcome.WINNER:
                winners += 1
            elif point.outcome == PointOutcome.ERROR:
                errors += 1

        for shot in point.shots:
            if shot.hitter != player:
                continue
            contact_locations.append((shot.contact_x, shot.contact_y))
            bounce_locations.append((shot.bounce_x, shot.bounce_y))
            if shot.shot_type == ShotType.SERVE:
                serve_speeds.append(shot.speed)
            elif shot.shot_type == ShotType.GROUNDSTROKE:
                groundstroke_speeds.append(shot.speed)

    return {
        "points_won": points_won,
        "winners": winners,
        "errors": errors,
        "avg_serve_speed": _avg(serve_speeds),
        "avg_groundstroke_speed": _avg(groundstroke_speeds),
        "contact_locations": contact_locations,
        "bounce_locations": bounce_locations,
    }
