# ScholarAI Interview Prep

## 60-Second Elevator Pitch

ScholarAI is a production-style Flask web application that helps Indian B.Tech students discover scholarships without manually searching multiple websites. I designed it with a modular architecture using Flask Blueprints, SQLAlchemy models, service layers, REST APIs, admin management, and a deterministic eligibility engine. A key design decision was keeping the backend as the source of truth for filtering, ranking, and eligibility scoring, while AI remains optional and only adds explanation layers later. That made the system more reliable, testable, and interview-friendly from a software engineering perspective.

## Architecture Explanation

ScholarAI follows a modular Flask architecture with an app factory, Blueprints, separate models, services, utilities, student views, admin views, and API routes. The data layer is normalized around scholarships, taxonomies, content, bookmarks, and activity logs. The service layer contains business rules such as search, recommendation scoring, analytics, and fraud checks. This separation keeps route handlers thin and makes the logic easier to test and extend.

## Why SQLite and Why PostgreSQL-Ready

SQLite is lightweight and perfect for local development, prototyping, and single-instance demos. But production traffic usually benefits from PostgreSQL because of better concurrency, reliability, and hosted-platform support. That is why the project starts with SQLite but is configured to accept hosted PostgreSQL URLs later.

## Why AI Is a Placeholder

I intentionally kept AI outside the core business logic. The platform still works fully without any AI API. Eligibility and recommendation logic are deterministic backend rules, while AI placeholders can later explain or summarize results. This prevents hallucinated scholarship data and keeps the platform trustworthy.

## Strong Resume Bullet Points

- Built a modular Flask scholarship portal with app-factory architecture, Blueprints, SQLAlchemy models, REST APIs, and admin workflows.
- Designed a normalized scholarship database with taxonomy tables, activity logging, notifications, and analytics-ready relationships.
- Implemented a deterministic eligibility and recommendation engine with weighted scoring, hard-rule gates, fraud checks, and deadline reminders.
- Added student-facing search, filtering, bookmarking, comparison, and eligibility-check flows with responsive Bootstrap UI.
- Prepared the application for deployment with Render-compatible startup, environment-based configuration, in-memory test configuration, and automated backend tests.

## Interview Questions You Should Be Ready For

- Why did you use Flask Blueprints instead of a single-file Flask app?
- How does your eligibility engine balance weighted scoring and hard-rule validation?
- Why did you normalize categories and states into separate tables?
- How would you migrate this system from SQLite to PostgreSQL?
- What security measures did you add for admin flows and APIs?
- Why did you keep AI separate from scholarship filtering and scoring?
- How would you improve search for large-scale scholarship data?
- How would you support real-time bookmarks across devices in the future?

## HR-Friendly Project Explanation

I built ScholarAI to solve a practical student problem: scholarship discovery is fragmented, repetitive, and hard to evaluate quickly. I focused on making the system feel like a real software product, not just a college assignment, by adding clean architecture, testing, deployment readiness, and a thoughtful user experience.
