import pytest
from datetime import datetime, timezone, timedelta
from services.risk_engine import (
    haversine_distance,
    get_severity_score,
    calculate_repeat_score,
    calculate_recency_score,
    classify_risk,
    compute_road_risk_score,
    generate_explanation
)


def test_haversine_distance():
    # Hyderabad Hitec City to Cyber Towers approx 150-200m
    lat1, lon1 = 17.4435, 78.3772
    lat2, lon2 = 17.4448, 78.3785
    dist = haversine_distance(lat1, lon1, lat2, lon2)
    assert 100 <= dist <= 300
    # Same point distance is 0
    assert haversine_distance(lat1, lon1, lat1, lon1) == 0.0


def test_severity_scores():
    assert get_severity_score("low") == 20.0
    assert get_severity_score("Medium") == 45.0
    assert get_severity_score("HIGH") == 75.0
    assert get_severity_score("critical") == 100.0
    # Unknown fallback
    assert get_severity_score("unknown") == 20.0


def test_repeat_score_capping():
    assert calculate_repeat_score(0) == 0.0
    assert calculate_repeat_score(1) == 25.0
    assert calculate_repeat_score(2) == 50.0
    assert calculate_repeat_score(3) == 75.0
    assert calculate_repeat_score(4) == 100.0
    assert calculate_repeat_score(10) == 100.0  # Properly capped at 100


def test_recency_decay():
    now = datetime.now(timezone.utc)
    # < 24 hours
    assert calculate_recency_score(now - timedelta(hours=2), now) == 100.0
    # 2 days (48 hrs)
    assert calculate_recency_score(now - timedelta(days=2), now) == 80.0
    # 5 days
    assert calculate_recency_score(now - timedelta(days=5), now) == 50.0
    # 10 days
    assert calculate_recency_score(now - timedelta(days=10), now) == 30.0
    # 20 days
    assert calculate_recency_score(now - timedelta(days=20), now) == 15.0
    # 40 days
    assert calculate_recency_score(now - timedelta(days=40), now) == 5.0


def test_risk_classification():
    assert classify_risk(15) == "Low"
    assert classify_risk(25) == "Medium"
    assert classify_risk(50) == "High"
    assert classify_risk(75) == "Critical"
    assert classify_risk(100) == "Critical"


def test_compute_road_risk_score():
    now = datetime.now(timezone.utc)
    
    # Critical severity (100 * 0.50 = 50) + 4 repeats (100 * 0.30 = 30) + 2 hrs recency (100 * 0.20 = 20) = 100.0
    result_crit = compute_road_risk_score("critical", 4, now - timedelta(hours=2), now)
    assert result_crit["score"] == 100.0
    assert result_crit["classification"] == "Critical"
    assert "Critical priority" in result_crit["explanation"]

    # Low severity (20 * 0.50 = 10) + 0 repeats (0 * 0.30 = 0) + 40 days (5 * 0.20 = 1) = 11.0
    result_low = compute_road_risk_score("low", 0, now - timedelta(days=40), now)
    assert result_low["score"] == 11.0
    assert result_low["classification"] == "Low"
    assert "Low priority" in result_low["explanation"]


def test_score_clamping():
    now = datetime.now(timezone.utc)
    res = compute_road_risk_score("critical", 100, now, now)
    assert 0.0 <= res["score"] <= 100.0
