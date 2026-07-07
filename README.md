# ScholarAI

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?logo=sqlalchemy&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-Portfolio_Ready-181717?logo=github&logoColor=white)

## Project Overview

ScholarAI is a Flask-based scholarship discovery portal built for Indian B.Tech students. The project focuses on practical scholarship search, structured filtering, eligibility scoring, deadline awareness, and admin-managed content workflows.

The application is designed with a backend-first approach: scholarship filtering, recommendation scoring, fraud checks, and eligibility evaluation are handled by deterministic Python logic and database-backed services. AI-related capabilities are present only as safe placeholder flows for future integration and do not replace backend business logic.

This repository is structured as a portfolio-quality full-stack Flask project with blueprints, service layers, SQLAlchemy models, public student pages, an admin panel, REST APIs, automated tests, and deployment-ready configuration.

## Features

- Public scholarship discovery with keyword search and structured filters
- Rule-based natural language query interpretation for scholarship search
- Scholarship detail pages with eligibility-related information
- Local bookmark and comparison experience for students without login
- Eligibility checker with backend scoring and recommendation results
- Dedicated trending scholarships and deadline reminder pages
- Scholarship news, FAQs, notifications, About, and Contact pages
- Admin login with protected dashboard routes
- Admin scholarship management with add, edit, delete, CSV import/export, and bulk actions
- Admin content management for news, FAQs, notifications, contact inbox, analytics, and settings
- REST APIs for scholarships, search, filters, comparison, content, analytics, eligibility, reminders, fraud checks, and AI placeholders
- SQLite database initialization with automatic table creation and starter seed data
- Automated unit and integration tests

## Tech Stack

- Backend: Python, Flask, Flask Blueprints
- Database: SQLite, SQLAlchemy
- Forms and Security: Flask-WTF, CSRF protection
- Frontend: HTML5, CSS3, Bootstrap 5, Vanilla JavaScript
- Deployment: Gunicorn, Render-ready configuration
- Testing: Python `unittest`

## Project Structure

```text
ScholarAI/
|-- app/
|   |-- admin/
|   |-- ai/
|   |-- api/
|   |-- auth/
|   |-- authentication/
|   |-- config/
|   |-- models/
|   |-- routes/
|   |-- services/
|   |-- static/
|   |   |-- css/
|   |   `-- js/
|   |-- student/
|   |-- templates/
|   `-- utils/
|-- database/
|   |-- init_db.py
|   `-- seed_admin.py
|-- docs/
|-- tests/
|-- app.py
|-- requirements.txt
|-- render.yaml
`-- wsgi.py
```

## Installation

```bash
git clone https://github.com/Kashish1924/ScholarAI
cd scholarAI
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Database Setup

Initialize the SQLite database, create all SQLAlchemy tables, and seed sample scholarship/content records when the database is empty:

```bash
python database/init_db.py
```

Create the first admin user:

```bash
python database/seed_admin.py
```

Default database location:

```text
database/scholarai.db
```

## Running the Project

Start the Flask application locally:

```bash
python app.py
```

Open the project in your browser:

```text
http://127.0.0.1:5000/
```

For production-style serving:

```bash
gunicorn wsgi:app
```

## Screenshots (leave placeholders)

- Home Page: `screenshots/home.png`
- Scholarship Listing: `screenshots/scholarships.png`
- Scholarship Detail: `screenshots/scholarship-detail.png`
- Eligibility Checker: `screenshots/eligibility-checker.png`
- Admin Dashboard: `screenshots/admin-dashboard.png`
- Analytics Dashboard: `screenshots/admin-analytics.png`
- Analytics Dashboard2: `screenshots/admin-analytics1.png`

## REST API Endpoints

Base URL:

```text
/api/v1
```

Status and Discovery:

- `GET /status`
- `GET /filters`
- `GET /search`
- `GET /search/suggestions`
- `GET /search/interpret`

Scholarships:

- `GET /scholarships`
- `GET /scholarships/<scholarship_id>`
- `POST /scholarships`
- `PUT /scholarships/<scholarship_id>`
- `DELETE /scholarships/<scholarship_id>`

Comparison and Discovery Utilities:

- `GET /comparison`
- `POST /comparison`
- `GET /trending`
- `GET /deadlines`
- `GET /deadline-reminders`
- `GET /fraud-checks`

Content:

- `GET /news`
- `GET /faqs`
- `GET /notifications`
- `POST /contact`

Eligibility and Recommendations:

- `POST /eligibility/check`
- `GET /recommendations`

Analytics:

- `GET /analytics`

Taxonomy:

- `GET /taxonomy/categories`
- `GET /taxonomy/states`
- `POST /taxonomy/categories`
- `POST /taxonomy/states`

AI Placeholder Endpoints:

- `POST /ai/chat`
- `GET /ai/scholarships/<scholarship_id>/summary`
- `GET /ai/comparison`
- `POST /ai/email`

## Testing

Run the automated test suite:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Current test coverage includes:

- API status, filters, search, eligibility, comparison, reminders, and fraud checks
- Service-layer eligibility and homepage section logic
- Taxonomy endpoint access control

## Future Improvements

- Replace placeholder sample scholarship links with verified live scholarship URLs
- Expand browser-level UI automation for bookmark and comparison interactions
- Add richer admin audit/reporting coverage
- Introduce PostgreSQL as the default production database option
- Integrate a real AI provider behind the existing placeholder interfaces

## Author

**Your Name Here**

- GitHub: `https://github.com/your-username`
- LinkedIn: `https://linkedin.com/in/your-profile`
