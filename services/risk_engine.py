"""
Road Risk Score Engine
Formula:
  ROAD RISK SCORE = (Severity Score * 0.50) + (Repeat Report Score * 0.30) + (Recency Score * 0.20)

Severity:
  - Low: 20
  - Medium: 45
  - High: 75
  - Critical: 100

Repeat Report Score:
  - Based on nearby existing reports within roughly ~500m radius (or matching location clusters).
  - Capped scale between 0 and 100:
    0 prior reports: 0
    1 prior: 25
    2 prior: 50
    3 prior: 75
    4+ prior: 100

Recency Score:
  - Within 24 hours: 100
  - 1 to 3 days: 80
  - 3 to 7 days: 50
  - 7 to 14 days: 30
  - 14 to 30 days: 15
  - > 30 days: 5

Clamped: 0 to 100.
Classification:
  - 0-24: Low
  - 25-49: Medium
  - 50-74: High
  - 75-100: Critical

DISCLAIMER:
  Experimental prioritization score for community road maintenance triage,
  not a scientifically validated accident prediction model.
"""

from datetime import datetime, timezone
import math

SEVERITY_WEIGHT = 0.50
REPEAT_WEIGHT = 0.30
RECENCY_WEIGHT = 0.20

SEVERITY_SCORES = {
    "low": 20.0,
    "medium": 45.0,
    "high": 75.0,
    "critical": 100.0
}


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in meters between two coordinates."""
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def get_severity_score(severity: str) -> float:
    clean_sev = str(severity).strip().lower()
    return SEVERITY_SCORES.get(clean_sev, 20.0)


def calculate_repeat_score(count_nearby_reports: int) -> float:
    """
    Score based on existing complaints in the vicinity (within ~500m).
    Capped between 0 and 100.
    """
    if count_nearby_reports <= 0:
        return 0.0
    elif count_nearby_reports == 1:
        return 25.0
    elif count_nearby_reports == 2:
        return 50.0
    elif count_nearby_reports == 3:
        return 75.0
    else:
        return 100.0


def calculate_recency_score(created_at: datetime, reference_time: datetime = None) -> float:
    """
    Decay function based on age of the report.
    """
    if reference_time is None:
        reference_time = datetime.now(timezone.utc)

    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    if reference_time.tzinfo is None:
        reference_time = reference_time.replace(tzinfo=timezone.utc)

    age_seconds = max(0, (reference_time - created_at).total_seconds())
    age_hours = age_seconds / 3600.0

    if age_hours <= 24:
        return 100.0
    elif age_hours <= 72:  # 1 to 3 days
        return 80.0
    elif age_hours <= 168:  # 3 to 7 days
        return 50.0
    elif age_hours <= 336:  # 7 to 14 days
        return 30.0
    elif age_hours <= 720:  # 14 to 30 days
        return 15.0
    else:
        return 5.0


def classify_risk(score: float) -> str:
    """Categorize numerical risk score into Low, Medium, High, or Critical."""
    if score >= 75:
        return "Critical"
    elif score >= 50:
        return "High"
    elif score >= 25:
        return "Medium"
    else:
        return "Low"


def generate_explanation(severity: str, repeat_count: int, recency_score: float, final_score: float) -> str:
    category = classify_risk(final_score)
    sev_desc = f"{severity.capitalize()} severity issue"
    
    if repeat_count == 0:
        rep_desc = "isolated report with no recent nearby complaints"
    elif repeat_count == 1:
        rep_desc = "1 additional nearby complaint recorded"
    else:
        rep_desc = f"{repeat_count} recurring nearby complaints"

    if recency_score >= 80:
        rec_desc = "fresh recent activity (within 72 hrs)"
    elif recency_score >= 50:
        rec_desc = "reported within the past week"
    else:
        rec_desc = "historical report with decaying urgency"

    return f"{category} priority: {sev_desc}, {rep_desc}, and {rec_desc}."


def compute_road_risk_score(severity: str,
                            repeat_count: int,
                            created_at: datetime,
                            reference_time: datetime = None) -> dict:
    """
    Calculates final composite score clamped between 0 and 100,
    along with breakdown details.
    """
    sev_score = get_severity_score(severity)
    rep_score = calculate_repeat_score(repeat_count)
    rec_score = calculate_recency_score(created_at, reference_time)

    raw_score = (sev_score * SEVERITY_WEIGHT) + (rep_score * REPEAT_WEIGHT) + (rec_score * RECENCY_WEIGHT)
    clamped_score = max(0.0, min(100.0, round(raw_score, 1)))
    classification = classify_risk(clamped_score)
    explanation = generate_explanation(severity, repeat_count, rec_score, clamped_score)

    return {
        "score": clamped_score,
        "classification": classification,
        "explanation": explanation,
        "components": {
            "severity_score": sev_score,
            "repeat_score": rep_score,
            "recency_score": rec_score,
            "repeat_count": repeat_count
        }
    }
