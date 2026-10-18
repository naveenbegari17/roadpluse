import os
import sqlite3
from datetime import datetime, timezone
from services.risk_engine import haversine_distance, compute_road_risk_score

DATABASE_PATH = os.environ.get("ROADPULSE_DB_PATH", os.path.join(os.path.dirname(__file__), "..", "roadpulse.db"))
DATABASE_URL = os.environ.get("DATABASE_URL")  # For PostgreSQL deployment (e.g. Supabase, Neon)


def get_connection():
    """
    Returns a database connection.
    Defaults to SQLite for local development and zero-cost setup.
    If DATABASE_URL is provided with postgres:// or postgresql://, uses psycopg2.
    """
    if DATABASE_URL and (DATABASE_URL.startswith("postgres://") or DATABASE_URL.startswith("postgresql://")):
        try:
            import psycopg2
            import psycopg2.extras
            # Fix postgres:// URL scheme compatibility with psycopg2
            url = DATABASE_URL
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            conn = psycopg2.connect(url, sslmode="require")
            return conn, "postgres"
        except Exception as e:
            print(f"[RoadPulse DB Warning] Failed to connect to PostgreSQL: {e}. Falling back to SQLite.")

    # SQLite fallback / default
    # Ensure directory exists if needed
    db_dir = os.path.dirname(os.path.abspath(DATABASE_PATH))
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn, "sqlite"


def init_db():
    """Initializes tables and populates sample data if table is empty."""
    conn, engine_type = get_connection()
    cur = conn.cursor()

    if engine_type == "postgres":
        cur.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                category VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                severity VARCHAR(50) NOT NULL,
                location_name VARCHAR(255) NOT NULL,
                latitude DOUBLE PRECISION NOT NULL,
                longitude DOUBLE PRECISION NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'Reported',
                road_risk_score DOUBLE PRECISION NOT NULL DEFAULT 0.0,
                risk_classification VARCHAR(50) NOT NULL DEFAULT 'Low',
                risk_explanation TEXT,
                is_sample BOOLEAN NOT NULL DEFAULT FALSE
            );
        """)
        conn.commit()
    else:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                severity TEXT NOT NULL,
                location_name TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Reported',
                road_risk_score REAL NOT NULL DEFAULT 0.0,
                risk_classification TEXT NOT NULL DEFAULT 'Low',
                risk_explanation TEXT,
                is_sample INTEGER NOT NULL DEFAULT 0
            );
        """)
        conn.commit()

    # Check if empty, seed demonstration data
    cur.execute("SELECT COUNT(*) FROM reports;")
    count = cur.fetchone()[0]
    if count == 0:
        seed_sample_data(conn, engine_type)

    cur.close()
    conn.close()


def seed_sample_data(conn, engine_type):
    """Seed initial demonstration records around Hyderabad, India clearly labeled as sample data."""
    sample_reports = [
        {
            "title": "Deep Pothole near Hitec City Metro Pillar 12",
            "category": "Pothole",
            "description": "Hazardous 8-inch pothole in the left bike lane causing sudden swerving during peak hours.",
            "severity": "Critical",
            "location_name": "Hitec City Main Road, Hyderabad",
            "latitude": 17.4435,
            "longitude": 78.3772,
            "created_at": "2026-10-18T10:30:00Z",
            "status": "In Progress"
        },
        {
            "title": "Severe Waterlogging under Begumpet Flyover",
            "category": "Waterlogging",
            "description": "Stagnant knee-deep water accumulation after overnight showers, submerging road divider.",
            "severity": "High",
            "location_name": "Begumpet Flyover, Hyderabad",
            "latitude": 17.4442,
            "longitude": 78.4682,
            "created_at": "2026-10-17T14:15:00Z",
            "status": "Reported"
        },
        {
            "title": "Broken High-Mast Streetlights on Outer Ring Road",
            "category": "Broken Streetlight",
            "description": "3 consecutive street lights non-functional creating dangerous dark zone on highway curve.",
            "severity": "Medium",
            "location_name": "Gachibowli Junction ORR, Hyderabad",
            "latitude": 17.4399,
            "longitude": 78.3489,
            "created_at": "2026-10-16T21:00:00Z",
            "status": "Under Review"
        },
        {
            "title": "Unpaved Dangerous Road Cut with Loose Gravel",
            "category": "Damaged Road",
            "description": "Pipeline excavation trench left uncovered with sharp debris and loose stones.",
            "severity": "High",
            "location_name": "Madhapur 100ft Road, Hyderabad",
            "latitude": 17.4486,
            "longitude": 78.3908,
            "created_at": "2026-10-18T08:00:00Z",
            "status": "Reported"
        },
        {
            "title": "Blind Curve with Missing Mirror and Damaged Divider",
            "category": "Dangerous Junction",
            "description": "Frequent near-misses due to overgrown shrubs and broken median on sharp intersection.",
            "severity": "Critical",
            "location_name": "Banjara Hills Road No. 12, Hyderabad",
            "latitude": 17.4156,
            "longitude": 78.4350,
            "created_at": "2026-10-15T18:45:00Z",
            "status": "Under Review"
        },
        {
            "title": "Secondary Pothole near Hitec City Cyber Towers",
            "category": "Pothole",
            "description": "Repeated complaint: Adjacent crater forming 150m away from Metro Pillar 12.",
            "severity": "High",
            "location_name": "Hitec City Main Road, Hyderabad",
            "latitude": 17.4448,
            "longitude": 78.3785,
            "created_at": "2026-10-18T16:00:00Z",
            "status": "Reported"
        },
        {
            "title": "Sinkhole Repaired at KPHB Colony 4th Phase",
            "category": "Damaged Road",
            "description": "Asphalt patched and leveled with fresh road markings completed.",
            "severity": "Low",
            "location_name": "KPHB Colony Phase 4, Hyderabad",
            "latitude": 17.4938,
            "longitude": 78.3986,
            "created_at": "2026-10-10T09:20:00Z",
            "status": "Resolved"
        }
    ]

    cur = conn.cursor()
    for item in sample_reports:
        # Calculate risk score
        dt = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
        # Repeat calculation for sample data (mocked baseline)
        repeat_count = 1 if "Hitec City" in item["location_name"] else 0
        computed = compute_road_risk_score(item["severity"], repeat_count, dt)

        if engine_type == "postgres":
            cur.execute("""
                INSERT INTO reports (
                    title, category, description, severity, location_name,
                    latitude, longitude, created_at, status, road_risk_score,
                    risk_classification, risk_explanation, is_sample
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE);
            """, (
                item["title"], item["category"], item["description"], item["severity"],
                item["location_name"], item["latitude"], item["longitude"], dt,
                item["status"], computed["score"], computed["classification"],
                computed["explanation"]
            ))
        else:
            cur.execute("""
                INSERT INTO reports (
                    title, category, description, severity, location_name,
                    latitude, longitude, created_at, status, road_risk_score,
                    risk_classification, risk_explanation, is_sample
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1);
            """, (
                item["title"], item["category"], item["description"], item["severity"],
                item["location_name"], item["latitude"], item["longitude"], item["created_at"],
                item["status"], computed["score"], computed["classification"],
                computed["explanation"]
            ))
    conn.commit()


def get_all_reports(category=None, severity=None, status=None):
    """Fetch reports with optional filtering."""
    conn, engine_type = get_connection()
    cur = conn.cursor()

    query = "SELECT * FROM reports WHERE 1=1"
    params = []

    placeholder = "%s" if engine_type == "postgres" else "?"

    if category:
        query += f" AND LOWER(category) = LOWER({placeholder})"
        params.append(category.strip())
    if severity:
        query += f" AND LOWER(severity) = LOWER({placeholder})"
        params.append(severity.strip())
    if status:
        query += f" AND LOWER(status) = LOWER({placeholder})"
        params.append(status.strip())

    query += " ORDER BY road_risk_score DESC, created_at DESC;"

    cur.execute(query, tuple(params))
    rows = cur.fetchall()

    reports = []
    for r in rows:
        reports.append(dict(r))

    cur.close()
    conn.close()
    return reports


def get_report_by_id(report_id: int):
    """Retrieve single report by primary key."""
    conn, engine_type = get_connection()
    cur = conn.cursor()
    placeholder = "%s" if engine_type == "postgres" else "?"
    cur.execute(f"SELECT * FROM reports WHERE id = {placeholder};", (report_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(row) if row else None


def count_nearby_reports(lat: float, lon: float, radius_meters: float = 500.0, exclude_id: int = None) -> int:
    """Find number of complaints within the spatial radius (~500m)."""
    conn, _ = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, latitude, longitude FROM reports;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    count = 0
    for r in rows:
        if exclude_id and r["id"] == exclude_id:
            continue
        dist = haversine_distance(lat, lon, float(r["latitude"]), float(r["longitude"]))
        if dist <= radius_meters:
            count += 1
    return count


def recalculate_nearby_scores(lat: float, lon: float, radius_meters: float = 500.0):
    """Recalculates risk score for any reports nearby that have gained an additional repeat report."""
    conn, engine_type = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, severity, created_at, latitude, longitude FROM reports;")
    all_reports = cur.fetchall()

    placeholder = "%s" if engine_type == "postgres" else "?"

    for rep in all_reports:
        rep_lat = float(rep["latitude"])
        rep_lon = float(rep["longitude"])
        dist = haversine_distance(lat, lon, rep_lat, rep_lon)
        if dist <= radius_meters:
            # Recompute repeat count for this report
            repeat_cnt = count_nearby_reports(rep_lat, rep_lon, radius_meters, exclude_id=rep["id"])
            created_dt = rep["created_at"]
            if isinstance(created_dt, str):
                created_dt = datetime.fromisoformat(created_dt.replace("Z", "+00:00"))

            computed = compute_road_risk_score(rep["severity"], repeat_cnt, created_dt)
            cur.execute(f"""
                UPDATE reports 
                SET road_risk_score = {placeholder},
                    risk_classification = {placeholder},
                    risk_explanation = {placeholder}
                WHERE id = {placeholder};
            """, (computed["score"], computed["classification"], computed["explanation"], rep["id"]))

    conn.commit()
    cur.close()
    conn.close()


def create_report(title: str, category: str, description: str, severity: str,
                  location_name: str, latitude: float, longitude: float) -> dict:
    """Validates, inserts a new road hazard report and triggers score calculations."""
    now_dt = datetime.now(timezone.utc)
    iso_now = now_dt.isoformat()

    # Calculate repeat complaints nearby prior to this one
    nearby_count = count_nearby_reports(latitude, longitude, radius_meters=500.0)
    computed = compute_road_risk_score(severity, nearby_count, now_dt)

    conn, engine_type = get_connection()
    cur = conn.cursor()

    if engine_type == "postgres":
        cur.execute("""
            INSERT INTO reports (
                title, category, description, severity, location_name,
                latitude, longitude, created_at, status, road_risk_score,
                risk_classification, risk_explanation, is_sample
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Reported', %s, %s, %s, FALSE)
            RETURNING id;
        """, (
            title, category, description, severity, location_name,
            latitude, longitude, now_dt, computed["score"],
            computed["classification"], computed["explanation"]
        ))
        new_id = cur.fetchone()[0]
    else:
        cur.execute("""
            INSERT INTO reports (
                title, category, description, severity, location_name,
                latitude, longitude, created_at, status, road_risk_score,
                risk_classification, risk_explanation, is_sample
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Reported', ?, ?, ?, 0);
        """, (
            title, category, description, severity, location_name,
            latitude, longitude, iso_now, computed["score"],
            computed["classification"], computed["explanation"]
        ))
        new_id = cur.lastrowid

    conn.commit()
    cur.close()
    conn.close()

    # Recalculate other reports in this cluster because a new complaint arrived
    recalculate_nearby_scores(latitude, longitude, radius_meters=500.0)

    return get_report_by_id(new_id)


def update_report_status(report_id: int, new_status: str) -> bool:
    """Allows demo/admin updating report lifecycle status."""
    valid_statuses = ["Reported", "Under Review", "In Progress", "Resolved"]
    if new_status not in valid_statuses:
        return False

    conn, engine_type = get_connection()
    cur = conn.cursor()
    placeholder = "%s" if engine_type == "postgres" else "?"
    cur.execute(f"UPDATE reports SET status = {placeholder} WHERE id = {placeholder};", (new_status, report_id))
    affected = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    return affected > 0


def get_dashboard_statistics():
    """Generates aggregate statistics for dashboard and analytics."""
    conn, _ = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM reports;")
    total_reports = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM reports WHERE LOWER(severity) = 'critical';")
    critical_hazards = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM reports WHERE road_risk_score >= 50.0;")
    high_risk_locations = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM reports WHERE LOWER(status) = 'resolved';")
    resolved_reports = cur.fetchone()[0]

    # Category breakdown
    cur.execute("SELECT category, COUNT(*) as count FROM reports GROUP BY category ORDER BY count DESC;")
    categories = [dict(r) for r in cur.fetchall()]

    # Severity breakdown
    cur.execute("SELECT severity, COUNT(*) as count FROM reports GROUP BY severity ORDER BY count DESC;")
    severities = [dict(r) for r in cur.fetchall()]

    # Status breakdown
    cur.execute("SELECT status, COUNT(*) as count FROM reports GROUP BY status ORDER BY count DESC;")
    statuses = [dict(r) for r in cur.fetchall()]

    # Risk score buckets (0-24, 25-49, 50-74, 75-100)
    cur.execute("SELECT risk_classification, COUNT(*) as count FROM reports GROUP BY risk_classification;")
    risk_distribution = [dict(r) for r in cur.fetchall()]

    # Top 5 locations with repeated complaints
    cur.execute("""
        SELECT location_name, COUNT(*) as report_count, AVG(road_risk_score) as avg_risk 
        FROM reports 
        GROUP BY location_name 
        ORDER BY report_count DESC, avg_risk DESC 
        LIMIT 5;
    """)
    top_recurring_locations = [dict(r) for r in cur.fetchall()]

    # Top 5 highest risk reports
    cur.execute("""
        SELECT id, title, location_name, category, severity, road_risk_score, status 
        FROM reports 
        ORDER BY road_risk_score DESC, created_at DESC 
        LIMIT 5;
    """)
    top_highest_risk = [dict(r) for r in cur.fetchall()]

    cur.close()
    conn.close()

    return {
        "total_reports": total_reports,
        "critical_hazards": critical_hazards,
        "high_risk_locations": high_risk_locations,
        "resolved_reports": resolved_reports,
        "categories": categories,
        "severities": severities,
        "statuses": statuses,
        "risk_distribution": risk_distribution,
        "top_recurring_locations": top_recurring_locations,
        "top_highest_risk": top_highest_risk
    }
