from app.analysis.stub import generate_fake_points
from app.court import SINGLES_COURT_LENGTH, SINGLES_COURT_WIDTH
from app.models import PointOutcome


def test_generates_requested_number_of_points():
    points = generate_fake_points(num_points=10, seed=42)
    assert len(points) == 10
    assert [p["index"] for p in points] == list(range(1, 11))


def test_shot_coordinates_within_court_bounds():
    points = generate_fake_points(num_points=15, seed=1)
    for point in points:
        for shot in point["shots"]:
            assert 0.0 <= shot["contact_x"] <= SINGLES_COURT_WIDTH
            assert 0.0 <= shot["contact_y"] <= SINGLES_COURT_LENGTH
            assert 0.0 <= shot["bounce_x"] <= SINGLES_COURT_WIDTH
            assert 0.0 <= shot["bounce_y"] <= SINGLES_COURT_LENGTH


def test_point_winner_matches_outcome_and_last_hitter():
    points = generate_fake_points(num_points=20, seed=7)
    for point in points:
        last_hitter = point["shots"][-1]["hitter"]
        if point["outcome"] == PointOutcome.WINNER:
            assert point["winner"] == last_hitter
        else:
            assert point["winner"] != last_hitter


def test_shot_times_are_monotonic_within_a_point():
    points = generate_fake_points(num_points=10, seed=99)
    for point in points:
        for shot in point["shots"]:
            assert shot["bounce_time"] > shot["contact_time"]
        for earlier, later in zip(point["shots"], point["shots"][1:]):
            assert later["contact_time"] >= earlier["bounce_time"]
