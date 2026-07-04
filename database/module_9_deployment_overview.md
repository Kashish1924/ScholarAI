# ScholarAI Module 9: Deployment Readiness

## Why This Module Matters

Production-quality projects need more than features and tests. They also need clear startup behavior, environment-based settings, deployment documentation, and safe defaults for hosted platforms.

## What Was Added

- Environment-based app startup in `app.py`
- Production WSGI entry point in `wsgi.py`
- `.env.example` for local setup
- Render deployment file `render.yaml`
- Production dependency additions for Gunicorn and PostgreSQL
- Configuration support for `.env` loading and hosted database URLs
- Expanded README and deployment guidance

## Production Notes

- Local development still works with SQLite
- Render can start with Gunicorn using `wsgi:app`
- If Render provides a PostgreSQL URL beginning with `postgres://`, the config normalizes it for SQLAlchemy
- Session cookies are secure in production mode

## SQLite Considerations

SQLite is acceptable for local development and simple demos, but it has limits for concurrent production traffic. For a stronger deployment story, use PostgreSQL on Render when possible.

## Environment Variables

- `FLASK_CONFIG`
- `SECRET_KEY`
- `DATABASE_URL`
- `PORT`

## Interview Talking Points

- Why separate `wsgi.py` from `app.py`: hosted WSGI servers should import an app object directly
- Why use environment-based config: it keeps local, test, and production behavior isolated
- Why recommend PostgreSQL over SQLite in production: better concurrency, reliability, and hosted-platform fit
