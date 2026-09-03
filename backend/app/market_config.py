DEMO_MARKET_DATA_VERSION = "demo-market-2026-09-v1"
MARKET_ANALYSIS_VERSION = "market-v1"

COMPETITION_RING_WEIGHTS = {"0_2": 12, "2_5": 6, "5_10": 2}
NEAREST_PRESSURE = ((0.5, 20), (1.0, 15), (2.0, 10), (5.0, 5))
SCORE_THRESHOLDS = ((25, "LOW"), (50, "MODERATE"), (75, "HIGH"), (101, "VERY_HIGH"))


def clamp_score(value: float) -> int:
    return max(0, min(100, round(value)))


def score_label(value: int) -> str:
    return next(label for upper, label in SCORE_THRESHOLDS if value < upper)


def competition_scores(ring_0_2: int, ring_2_5: int, ring_5_10: int, nearest_km):
    pressure = 0
    if nearest_km is not None:
        for upper, points in NEAREST_PRESSURE:
            if nearest_km < upper:
                pressure = points
                break
    intensity = clamp_score(ring_0_2 * COMPETITION_RING_WEIGHTS["0_2"] + ring_2_5 * COMPETITION_RING_WEIGHTS["2_5"] + ring_5_10 * COMPETITION_RING_WEIGHTS["5_10"] + pressure)
    return intensity, 100 - intensity
