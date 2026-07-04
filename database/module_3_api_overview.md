# ScholarAI Module 3: Backend Service and API Foundation

## Why This Module Matters

Module 2 defined the data structure. Module 3 makes that data usable by the application. In production systems, models alone are not enough. We also need:

- validation to stop bad data before it reaches the database
- service classes to keep business logic out of route files
- consistent JSON responses for frontend integration
- CRUD endpoints that can be extended safely over time

## Architectural Decisions

- Routes handle HTTP concerns only
- Services handle scholarship business logic
- Validators clean and verify incoming payloads
- Utility helpers keep response formatting reusable

This keeps the project aligned with MVC and clean architecture principles.

## Implemented Endpoints

### Health

- `GET /api/v1/status`

### Scholarship CRUD

- `GET /api/v1/scholarships`
- `GET /api/v1/scholarships/<id>`
- `POST /api/v1/scholarships`
- `PUT /api/v1/scholarships/<id>`
- `DELETE /api/v1/scholarships/<id>`

### Taxonomy Seed Helpers

- `POST /api/v1/taxonomy/categories`
- `POST /api/v1/taxonomy/states`

These taxonomy endpoints are important because scholarships reference categories and states through foreign-key relationships.

## Supported Scholarship Filters

- `keyword`
- `scholarship_type`
- `state_code`
- `category_slug`
- `gender`
- `degree`
- `branch`
- `academic_year`
- `max_income`
- `min_cgpa`
- `is_featured`
- `deadline_within_days`
- `status`
- `page`
- `per_page`

## Example Create Payload

```json
{
  "scholarship_name": "AICTE Pragati Scholarship",
  "provider_name": "AICTE",
  "scholarship_type": "government",
  "scholarship_amount": 50000,
  "eligibility_description": "For eligible female students in technical education.",
  "degree": "B.Tech",
  "branch": "CSE",
  "academic_year": "1",
  "application_link": "https://example.com/apply",
  "official_website": "https://example.com",
  "application_end_date": "2026-08-31",
  "description": "Financial support for technical education.",
  "categories": ["general", "obc"],
  "states": ["DL", "MH"]
}
```

## Response Pattern

Every API follows a consistent shape:

```json
{
  "status": "success",
  "message": "Scholarship created successfully.",
  "data": {}
}
```

Validation failures return:

```json
{
  "status": "error",
  "message": "Scholarship validation failed.",
  "errors": {
    "field_name": ["Problem description"]
  }
}
```

## Security Notes

- API payloads are validated before persistence
- URLs are checked for valid HTTP or HTTPS format
- Unsupported fields are rejected during updates
- Database relationships protect category and state references
- CSRF remains enabled globally, while the API blueprint is exempted so JSON clients can function without form tokens

## Complexity Notes

- Basic lookup by primary key: `O(1)` average with indexed primary keys
- Filtered scholarship search: depends on the query combination, but indexed columns reduce scan cost significantly
- Slug generation: `O(k)` where `k` is the number of collisions for the same base slug

## Real-World Improvements

- Add Alembic migrations
- Add authentication and role checks for admin-only APIs
- Add request schema tooling such as Marshmallow or Pydantic
- Add automated API tests with pytest
- Add bulk create, bulk update, CSV import, and soft delete workflows
