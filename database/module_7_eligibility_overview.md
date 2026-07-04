# ScholarAI Module 7: Eligibility and Recommendation Engine

## Why This Module Matters

This module is the core of the product. Students should not manually inspect dozens of scholarship pages. Instead, they provide profile data and the backend calculates which scholarships fit them best.

## What Was Added

- Deterministic eligibility scoring engine
- Eligible, partially eligible, and not eligible classification
- Backend recommendation API endpoints
- Rule-based fraud checks
- Deadline reminder buckets
- Student eligibility checker page wired to the backend
- AI explanation placeholder layered on top of backend-calculated results

## Scoring Weights

- Income Match = 25
- Category Match = 20
- State Match = 15
- Degree Match = 10
- Branch Match = 10
- CGPA Match = 10
- Gender Match = 5
- Minority Match = 3
- Disability Match = 2

## Design Principles

- The backend calculates all recommendation logic
- AI does not perform filtering or scoring
- Hard requirements such as academic year, hosteller rules, and day-scholar rules can block eligibility even if the score is otherwise high
- Deadline urgency is used as a ranking factor after eligibility is calculated

## Endpoints Added

- `POST /api/v1/eligibility/check`
- `GET /api/v1/recommendations`
- `GET /api/v1/deadline-reminders`
- `GET /api/v1/fraud-checks`

## Security Notes

- All eligibility inputs are validated
- Fraud checks are rule-based and predictable
- AI explanation remains a harmless placeholder and never overrides backend results

## Interview Talking Points

- Why keep AI separate from eligibility: business correctness must remain deterministic
- Why use weighted scoring: it provides explainable ranking rather than only yes-or-no filtering
- Why still keep hard requirement gates: some scholarship rules should not be softened by partial scoring
