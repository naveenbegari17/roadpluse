import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from database.db import (
    init_db,
    get_all_reports,
    get_report_by_id,
    create_report,
    update_report_status,
    get_dashboard_statistics
)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "roadpulse_dev_zero_cost_secret_2026")

# Initialize database tables & seed data on launch
with app.app_context():
    try:
        init_db()
    except Exception as e:
        print(f"[RoadPulse DB Initialization] Error: {e}")


# --- HTML PAGE ROUTES ---

@app.route("/")
def index():
    stats = get_dashboard_statistics()
    recent_reports = get_all_reports()[:6]
    return render_template("index.html", stats=stats, recent_reports=recent_reports)


@app.route("/map")
def live_map():
    return render_template("map.html")


@app.route("/report", methods=["GET", "POST"])
def report_hazard():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        severity = request.form.get("severity", "").strip()
        location_name = request.form.get("location_name", "").strip()
        lat_raw = request.form.get("latitude", "").strip()
        lon_raw = request.form.get("longitude", "").strip()

        errors = []
        if not title:
            errors.append("Hazard title is required.")
        if category not in ["Pothole", "Damaged Road", "Broken Streetlight", "Waterlogging", "Dangerous Junction", "Other"]:
            errors.append("Please select a valid hazard category.")
        if not description:
            errors.append("Description is required.")
        if severity not in ["Low", "Medium", "High", "Critical"]:
            errors.append("Please choose a valid severity level.")
        if not location_name:
            errors.append("Location description or landmark is required.")

        try:
            latitude = float(lat_raw)
            longitude = float(lon_raw)
            if not (-90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0):
                errors.append("Invalid GPS coordinate values.")
        except (ValueError, TypeError):
            errors.append("Valid Latitude and Longitude coordinates are required. Click on the map to pin.")

        if errors:
            for err in errors:
                flash(err, "error")
            return render_template("report.html", form_data=request.form)

        try:
            new_report = create_report(
                title=title,
                category=category,
                description=description,
                severity=severity,
                location_name=location_name,
                latitude=latitude,
                longitude=longitude
            )
            flash(f"Road hazard successfully reported! Computed Road Risk Score: {new_report['road_risk_score']}/100 ({new_report['risk_classification']}).", "success")
            return redirect(url_for("report_details", report_id=new_report["id"]))
        except Exception as e:
            flash(f"Database error while saving report: {str(e)}", "error")
            return render_template("report.html", form_data=request.form)

    return render_template("report.html", form_data={})


@app.route("/analytics")
def analytics():
    stats = get_dashboard_statistics()
    return render_template("analytics.html", stats=stats)


@app.route("/report/<int:report_id>")
def report_details(report_id):
    report = get_report_by_id(report_id)
    if not report:
        flash("Hazard report not found.", "error")
        return redirect(url_for("live_map"))
    return render_template("report_details.html", report=report)


@app.route("/report/<int:report_id>/update-status", methods=["POST"])
def update_status(report_id):
    new_status = request.form.get("status", "").strip()
    # Demonstration / Prototype mechanism
    admin_token = request.form.get("admin_token", "").strip()
    
    # Simple zero-cost demo safeguard to prevent unauthorized random changes
    if admin_token != "DEMO_ADMIN":
        flash("Demo Admin key required to change report lifecycle status (Enter 'DEMO_ADMIN' in field).", "error")
        return redirect(url_for("report_details", report_id=report_id))

    if update_report_status(report_id, new_status):
        flash(f"Report status updated to '{new_status}'.", "success")
    else:
        flash("Failed to update status. Invalid status option provided.", "error")

    return redirect(url_for("report_details", report_id=report_id))


@app.route("/aws-architecture")
def aws_architecture():
    return render_template("aws_architecture.html")


@app.route("/about")
def about():
    return render_template("about.html")


# --- JSON API ENDPOINTS FOR LEAFLET & CHART.JS ---

@app.route("/api/reports")
def api_reports():
    category = request.args.get("category")
    severity = request.args.get("severity")
    status = request.args.get("status")
    reports = get_all_reports(category=category, severity=severity, status=status)
    return jsonify({
        "status": "success",
        "count": len(reports),
        "data": reports
    })


@app.route("/api/analytics")
def api_analytics():
    stats = get_dashboard_statistics()
    return jsonify({
        "status": "success",
        "data": stats
    })


# --- ERROR HANDLERS ---

@app.errorhandler(404)
def page_not_found(e):
    return render_template("base.html", error_title="404 - Page Not Found",
                           error_message="The requested RoadPulse page or hazard record does not exist."), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("base.html", error_title="500 - Server Error",
                           error_message="An internal server error occurred while processing the road safety data."), 500


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
