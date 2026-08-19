from types import SimpleNamespace

from app.models import Player, PointOutcome, ShotType
from app.stats import compute_player_stats


def _shot(hitter, shot_type, speed, contact=(1.0, 1.0), bounce=(2.0, 2.0)):
    return SimpleNamespace(
        hitter=hitter,
        shot_type=shot_type,
        speed=speed,
        contact_x=contact[0],
        contact_y=contact[1],
        bounce_x=bounce[0],
        bounce_y=bounce[1],
    )


def _point(winner, outcome, shots):
    return SimpleNamespace(winner=winner, outcome=outcome, shots=shots)


def test_points_won_and_winner_error_attribution():
    points = [
        _point(
            Player.PLAYER_1,
            PointOutcome.WINNER,
            [
                _shot(Player.PLAYER_1, ShotType.SERVE, 40.0),
                _shot(Player.PLAYER_2, ShotType.GROUNDSTROKE, 20.0),
                _shot(Player.PLAYER_1, ShotType.GROUNDSTROKE, 25.0),
            ],
        ),
        _point(
            Player.PLAYER_1,
            PointOutcome.ERROR,
            [
                _shot(Player.PLAYER_1, ShotType.SERVE, 45.0),
                _shot(Player.PLAYER_2, ShotType.GROUNDSTROKE, 22.0),
            ],
        ),
    ]

    p1_stats = compute_player_stats(points, Player.PLAYER_1)
    p2_stats = compute_player_stats(points, Player.PLAYER_2)

    assert p1_stats["points_won"] == 2
    assert p1_stats["winners"] == 1  # final shot of point 1
    assert p1_stats["errors"] == 0
    assert p2_stats["errors"] == 1  # final shot of point 2 was player2's unforced error
    assert p2_stats["winners"] == 0

    assert p1_stats["avg_serve_speed"] == 42.5
    assert p1_stats["avg_groundstroke_speed"] == 25.0
    assert p2_stats["avg_groundstroke_speed"] == 21.0
