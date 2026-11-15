from trips.domain.metrics import RouteMetrics
from trips.domain.recommendation import RouteOption, rank_routes
from trips.domain.risk import RiskLevel


def make_option(
    route_id: str,
    *,
    no_travel: float = 0,
    severe: float = 0,
    high: float = 0,
    average_risk: float = 1.0,
    duration_s: float = 100,
) -> RouteOption:
    miles = {level: 0.0 for level in RiskLevel}
    miles[RiskLevel.NO_TRAVEL] = no_travel
    miles[RiskLevel.SEVERE] = severe
    miles[RiskLevel.HIGH] = high
    metrics = RouteMetrics(100, miles, average_risk)
    return RouteOption(route_id, metrics, duration_s)


def ranked_ids(options: list[RouteOption]) -> list[str]:
    return [ranked.option.route_id for ranked in rank_routes(options)]


def test_no_travel_miles_decide_first():
    worse = make_option("worse", no_travel=2, severe=0, high=0, average_risk=0, duration_s=1)
    better = make_option("better", no_travel=1, severe=50, high=50, average_risk=4, duration_s=9)
    assert ranked_ids([worse, better]) == ["better", "worse"]


def test_severe_miles_decide_when_no_travel_equal():
    worse = make_option("worse", severe=2, high=0, average_risk=0, duration_s=1)
    better = make_option("better", severe=1, high=50, average_risk=4, duration_s=9)
    assert ranked_ids([worse, better]) == ["better", "worse"]


def test_high_miles_decide_when_severe_equal():
    worse = make_option("worse", high=2, average_risk=0, duration_s=1)
    better = make_option("better", high=1, average_risk=4, duration_s=9)
    assert ranked_ids([worse, better]) == ["better", "worse"]


def test_average_risk_decides_when_high_equal():
    worse = make_option("worse", average_risk=2, duration_s=1)
    better = make_option("better", average_risk=1, duration_s=9)
    assert ranked_ids([worse, better]) == ["better", "worse"]


def test_duration_decides_when_risk_equal():
    worse = make_option("worse", duration_s=200)
    better = make_option("better", duration_s=100)
    assert ranked_ids([worse, better]) == ["better", "worse"]


def test_negligible_risk_difference_falls_through_to_duration():
    slower = make_option("slower", average_risk=1.0, duration_s=200)
    faster = make_option("faster", average_risk=1.0 + 1e-10, duration_s=100)
    assert ranked_ids([slower, faster]) == ["faster", "slower"]


def test_exact_ties_keep_input_order():
    options = [make_option("a"), make_option("b"), make_option("c")]
    assert ranked_ids(options) == ["a", "b", "c"]


def test_single_route_is_recommended_rank_one():
    [ranked] = rank_routes([make_option("only")])
    assert (ranked.rank, ranked.recommended) == (1, True)


def test_empty_input_gives_empty_list():
    assert rank_routes([]) == []


def test_no_travel_routes_stay_in_list_and_are_flagged():
    blocked = make_option("blocked", no_travel=3)
    clear = make_option("clear")
    ranked = rank_routes([blocked, clear])
    assert [r.option.route_id for r in ranked] == ["clear", "blocked"]
    assert [r.has_no_travel for r in ranked] == [False, True]


def test_only_first_is_recommended():
    options = [make_option("a", duration_s=3), make_option("b", duration_s=1), make_option("c")]
    assert [r.recommended for r in rank_routes(options)] == [True, False, False]


def test_ranks_are_one_based_and_consecutive():
    options = [make_option("a", high=3), make_option("b", high=1), make_option("c", high=2)]
    assert [r.rank for r in rank_routes(options)] == [1, 2, 3]
