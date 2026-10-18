# RoadPulse — Roads That Speak
### Zero-Cost Citizen-Powered Road Safety Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Backend-Flask-green.svg)](https://flask.palletsprojects.com/)
[![Leaflet](https://img.shields.io/badge/Map-Leaflet%201.9-brightgreen.svg)](https://leafletjs.com/)
[![License](https://img.shields.io/badge/Budget-%E2%82%B90%20Zero--Cost-orange.svg)](#)
[![Deployment](https://img.shields.io/badge/Deploy-Vercel%20Serverless-black.svg)](https://vercel.com)

RoadPulse is an open-source, citizen-powered road hazard reporting and risk scoring web application built for college project demonstrations and community advocacy. Citizens can pinpoint potholes, broken streetlights, waterlogged roads, and hazardous intersections on an interactive Leaflet/OpenStreetMap map.

The platform automatically computes a **Road Risk Score (0–100)** to triage which problem areas may need immediate attention based on severity, repeat neighborhood complaints, and recency.

---

## 1. Features Overview

* **Zero-Cost Design (₹0 Total Budget)**: Built completely using free, open-source software (Python, Flask, Leaflet, OpenStreetMap tiles, Chart.js). No paid APIs or credit cards required.
* **Interactive Live Map**: Pin and view road hazard markers color-coded by priority with interactive filtering by category, severity, and resolution status.
* **Road Risk Score Engine**: An objective, modular Python scoring engine implementing spatial Haversine clustering (~500m radius) and recency decay.
* **Citywide Analytics**: Chart.js visualizations showing category distribution, severity breakdown, lifecycle status, and top 5 recurring complaint hotspots.
* **Restricted Demo Administration**: Safe status management (`Reported`, `Under Review`, `In Progress`, `Resolved`) protected with a demonstration passkey (`DEMO_ADMIN`).
* **AWS Cloud Learning Blueprint**: A dedicated educational guide detailing how this prototype maps to enterprise AWS services (CloudFront, API Gateway, Lambda, RDS/Aurora, S3, CloudWatch, and IAM).

---

## 2. Technology Stack

* **Frontend**: HTML5, CSS3 (Custom Civic-Tech Design System in `style.css`), Vanilla JavaScript.
* **Backend**: Python 3, Flask.
* **Mapping**: Leaflet.js and OpenStreetMap (OSM) public tiles (in compliance with usage policy).
* **Data Visualization**: Chart.js.
* **Database**:
  * Local Development: Zero-cost SQLite (`roadpulse.db`).
  * Cloud Serverless Deployment: Free PostgreSQL connection string support (Neon, Supabase) via `DATABASE_URL`.
* **Testing**: `pytest` automated test suite.
* **Deployment Target**: Vercel Serverless Python runtime.

---

## 3. Project Folder Structure

```
roadpulse/
├── app.py                      # Core Flask application & API routes
├── requirements.txt            # Python dependencies (Flask, pytest, psycopg2-binary)
├── vercel.json                 # Vercel serverless routing configuration
├── README.md                   # Complete beginner guide & documentation
├── .gitignore                  # Git ignore rules protecting databases & secrets
├── .env.example                # Environment variables reference template
├── api/
│   └── index.py                # Vercel Serverless WSGI Handler entry point
├── services/
│   └── risk_engine.py          # Road Risk Score calculation & clustering engine
├── database/
│   └── db.py                   # Modular DB layer (SQLite & PostgreSQL support)
├── templates/
│   ├── base.html               # Base layout, navbar & civic footer
│   ├── index.html              # Homepage hero, stats cards & recent reports
│   ├── report.html             # Hazard report submission form with map pin picker
│   ├── map.html                # Interactive Live Map with filter sidebar & legend
│   ├── analytics.html          # Chart.js analytics & recurring hotspot tables
│   ├── report_details.html     # Single report view, risk breakdown & demo status update
│   ├── aws_architecture.html   # Educational AWS Cloud architecture blueprint
│   └── about.html              # Methodology, formula explanation & disclaimers
├── static/
│   ├── css/
│   │   └── style.css           # Civic-tech styling, cards, badges & responsive styles
│   └── js/
│       ├── map.js              # Leaflet dynamic marker rendering & filters
│       └── analytics.js        # Chart.js initialization with real backend metrics
└── tests/
    ├── test_risk_engine.py     # Unit tests for scoring, decay & clustering
    └── test_app.py             # Integration tests for Flask routes & validation
```

---

## 4. Road Risk Scoring Formula

The risk engine (`services/risk_engine.py`) prioritizes hazards using the formula:

$$\text{ROAD RISK SCORE} = (\text{Severity Score} \times 0.50) + (\text{Repeat Report Score} \times 0.30) + (\text{Recency Score} \times 0.20)$$

### 1. Severity Score (50% Weight)
* **Low**: 20 points
* **Medium**: 45 points
* **High**: 75 points
* **Critical**: 100 points

### 2. Repeat Report Score (30% Weight)
Calculates complaints within a spatial radius of **~500 meters** using the Haversine distance formula:
* 0 prior complaints: 0 points
* 1 prior complaint: 25 points
* 2 prior complaints: 50 points
* 3 prior complaints: 75 points
* 4+ prior complaints: 100 points (capped to prevent infinite gaming)

### 3. Recency Decay Score (20% Weight)
* Within 24 hours: 100 points
* 1 to 3 days: 80 points
* 3 to 7 days: 50 points
* 7 to 14 days: 30 points
* 14 to 30 days: 15 points
* Over 30 days: 5 points

### Final Clamped Classification
* **0–24**: Low Priority (Green)
* **25–49**: Medium Priority (Yellow)
* **50–74**: High Priority (Orange)
* **75–100**: Critical Priority (Red)

> **Important Academic Disclaimer**: This score is an experimental prioritization metric for community triage and does not scientifically predict traffic collisions or represent official municipal endorsement.

---

## 5. Running the Project Locally (Windows PowerShell)

As a beginner, follow these exact steps in your terminal:

### Step 1: Clone or Open Project Directory
```powershell
cd C:\Users\navee\OneDrive\Desktop\roadpluse
```

### Step 2: (Recommended) Create & Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If PowerShell shows an execution policy error, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

### Step 3: Install Required Packages
```powershell
python -m pip install -r requirements.txt
```

### Step 4: Run the Flask Application
```powershell
python app.py
```
Open your browser and navigate to: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 6. Running Automated Unit Tests

Execute the full test suite using `pytest`:

```powershell
python -m pytest tests/ -v
```

All 14 unit and integration tests will execute, verifying scoring accuracy, decay curves, coordinate validation, and web route handlers.

---

## 7. Zero-Cost Persistent PostgreSQL Database (Optional for Cloud)

### Why is this needed for Vercel?
Vercel is a **serverless** platform. Its serverless functions are stateless and spin down when idle. Any SQLite file saved inside Vercel's temporary filesystem will be erased between serverless restarts.

To retain user-submitted reports permanently online for ₹0:

1. Sign up for a free cloud PostgreSQL provider:
   * **[Neon.tech](https://neon.tech)** (Generous free tier serverless Postgres)
   * OR **[Supabase.com](https://supabase.com)** (Free tier Postgres project)
2. Copy your connection URL (e.g., `postgresql://user:password@ep-sample.us-east-2.aws.neon.tech/neondb?sslmode=require`).
3. Add this connection URL as an environment variable named `DATABASE_URL` in Vercel.

*If you do not configure `DATABASE_URL`, RoadPulse will gracefully fallback to SQLite and automatically re-seed sample demonstration reports whenever invoked.*

---

## 8. Step-by-Step GitHub Upload Guide

Run the following commands in Windows PowerShell:

```powershell
# 1. Initialize git
git init

# 2. Add all project files (safe .gitignore prevents database or secret exposure)
git add .

# 3. Create your initial commit
git commit -m "feat: complete RoadPulse zero-cost platform"

# 4. Rename default branch to main
git branch -M main

# 5. Link to your GitHub repository (Create a new repository on github.com first)
git remote add origin https://github.com/YOUR_USERNAME/roadpulse.git

# 6. Push code to GitHub
git push -u origin main
```

---

## 9. Step-by-Step Vercel Deployment Guide

1. Go to **[vercel.com](https://vercel.com)** and sign in with your GitHub account.
2. Click **"Add New"** > **"Project"**.
3. Select your `roadpulse` repository and click **Import**.
4. In the Project Configuration screen:
   * **Framework Preset**: Other
   * **Root Directory**: `./` (default)
5. Expand the **Environment Variables** section and configure:
   * `FLASK_SECRET_KEY`: Enter a random secret string (e.g. `roadpulse_secret_key_2026`).
   * (Optional) `DATABASE_URL`: Your free Neon or Supabase PostgreSQL connection string.
6. Click **Deploy**.
7. Vercel will build your Python application and provide a free live URL (e.g. `https://roadpulse.vercel.app`).

---

## 10. Educational AWS Architecture Mapping

The `/aws-architecture` page on the website visualizes how RoadPulse maps to AWS services:

| Component | Prototype Implementation | Production AWS Serverless Equivalent | Official Documentation |
| :--- | :--- | :--- | :--- |
| **Static Delivery & CDN** | Local Static / Vercel Edge | **Amazon CloudFront** | [CloudFront Docs](https://aws.amazon.com/cloudfront/) |
| **API & Routing** | Flask (`app.py`) | **Amazon API Gateway** | [API Gateway Docs](https://aws.amazon.com/api-gateway/) |
| **Compute / Risk Engine** | Python WSGI | **AWS Lambda** (Python 3.12) | [AWS Lambda Docs](https://aws.amazon.com/lambda/) |
| **Database** | SQLite / Free PostgreSQL | **Amazon Aurora / RDS (PostgreSQL)** | [Amazon RDS Docs](https://aws.amazon.com/rds/) |
| **Photo Uploads** | Omitted for ₹0 budget | **Amazon S3** (Presigned URLs) | [Amazon S3 Docs](https://aws.amazon.com/s3/) |
| **Monitoring & Alarms** | Python console logs | **Amazon CloudWatch** | [CloudWatch Docs](https://aws.amazon.com/cloudwatch/) |
| **Security & Permissions** | Environment variables | **AWS IAM** | [AWS IAM Docs](https://aws.amazon.com/iam/) |

---

## 11. Troubleshooting Common Issues

* **Leaflet Map Not Loading Tiles**: Check your internet connection. RoadPulse uses OpenStreetMap public tiles requiring standard HTTPS network access.
* **Database Reset on Vercel**: As noted above, configure a free cloud PostgreSQL connection string via the `DATABASE_URL` environment variable in Vercel to preserve submitted reports across serverless cold starts.
* **Permission Denied on PowerShell Script Activation**: Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in your PowerShell session.
* **Demo Status Update Rejected**: The status update form requires the demonstration passkey `DEMO_ADMIN` to prevent accidental public edits during student presentations.

---

## 12. License & Academic Attribution
Developed as an open-source civic technology platform for educational demonstrations and academic review.
RoadPulse &copy; 2026. Built with Python, Flask, Leaflet, and OpenStreetMap.
