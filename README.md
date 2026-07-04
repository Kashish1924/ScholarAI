# ScholarAI

ScholarAI is an AI-ready scholarship finder portal for Indian B.Tech students. It helps students discover relevant scholarships using backend eligibility rules, structured filters, recommendation scoring, deadline tracking, and admin-managed scholarship data.

The application is designed so the backend remains the source of truth. AI is optional and currently kept as safe placeholders only.

## Features

- Public scholarship discovery with filters
- Scholarship detail pages
- Local bookmarks and comparison
- Backend eligibility scoring engine
- Deadline reminders
- Rule-based fraud checks
- Admin login and scholarship management
- REST APIs for scholarships, search, filters, content, analytics, and recommendations

## Tech Stack

- Frontend: HTML5, CSS3, Bootstrap 5, Vanilla JavaScript
- Backend: Python, Flask, Flask Blueprints
- Database: SQLite for local development, PostgreSQL-ready for hosted deployment
- Deployment: Render, Gunicorn
- AI: Placeholder-only service functions for later Gemini integration

## Project Structure

```text
app/
  admin/
  ai/
  api/
  authentication/
  config/
  models/
  routes/
  services/
  static/
  student/
  templates/
  utils/
database/
tests/
```

## Local Setup

```bash
pip install -r requirements.txt
copy .env.example .env
python database/init_db.py
python app.py
```

Open `http://127.0.0.1:5000/`.

## Initial Admin Setup

```bash
python database/seed_admin.py
```

## Run Tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Environment Variables

- `FLASK_CONFIG`: `development`, `testing`, or `production`
- `SECRET_KEY`: required for secure sessions and forms
- `DATABASE_URL`: SQLite locally, PostgreSQL recommended in production
- `PORT`: runtime port for hosted environments

Example values are provided in [.env.example](C:/Users/DELL/OneDrive/Pictures/Documents/scholarAI/.env.example).

## Render Deployment

This repository includes [render.yaml](C:/Users/DELL/OneDrive/Pictures/Documents/scholarAI/render.yaml) and [wsgi.py](C:/Users/DELL/OneDrive/Pictures/Documents/scholarAI/wsgi.py).

Recommended Render flow:

1. Push the repository to GitHub.
2. Create a new Render web service from the repository.
3. Use the included `render.yaml`, or set:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn wsgi:app`
4. Add environment variables:
   - `FLASK_CONFIG=production`
   - `SECRET_KEY=<strong-random-value>`
   - `DATABASE_URL=<render-postgresql-url-or-sqlite-path>`

## SQLite and PostgreSQL Notes

- SQLite is fine for local development, demos, and small single-instance setups.
- For production-like deployment, PostgreSQL is a better choice because it handles concurrency and hosted environments more reliably.
- The config automatically normalizes `postgres://` URLs to the SQLAlchemy-friendly `postgresql://` format.

## API Overview

Main backend capabilities include:

- Scholarship CRUD
- Search and filter endpoints
- Comparison endpoints
- Trending, news, FAQ, and notification endpoints
- Analytics summary
- Eligibility and recommendation endpoints
- Deadline reminder and fraud-check endpoints

## AI Integration Policy

- No OpenAI or Gemini SDK is currently installed
- No API keys are required for the app to run
- AI placeholder functions live in [app/ai/ai_service.py](C:/Users/DELL/OneDrive/Pictures/Documents/scholarAI/app/ai/ai_service.py)
- The platform remains functional even if AI is never integrated

## Deployment Checklist

- Set a strong `SECRET_KEY`
- Choose the correct `FLASK_CONFIG`
- Initialize the database
- Seed the first admin user
- Run automated tests
- Verify admin login, scholarship listing, and eligibility endpoints

## Future Scope

- CSV import and export UI polish
- AI-powered natural-language explanations using Gemini
- Chart-based analytics dashboard enhancements
- Browser tests and CI pipeline
- PostgreSQL-first production deployment

## License

This project is prepared as a portfolio-quality educational and production-style sample application.
