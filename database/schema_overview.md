# ScholarAI Module 2: Database Design

## Why Normalization Matters

Normalization reduces duplicate data, keeps updates consistent, and makes the backend easier to maintain. For ScholarAI, that matters because the same category or state may appear across many scholarships. Instead of storing repeated text everywhere, we keep shared master data in dedicated tables and connect it using foreign keys.

This design primarily follows:

- First Normal Form (1NF): every column stores atomic values
- Second Normal Form (2NF): non-key attributes depend on the full primary key
- Third Normal Form (3NF): descriptive lookup data like categories and states is separated from scholarship records

## Why Each Table Exists

- `admins`: secure administrative users for dashboard access and management actions
- `scholarships`: the canonical scholarship record used by search, filters, eligibility, and analytics
- `categories`: reusable category master data such as SC, ST, OBC, General, Merit
- `states`: reusable Indian state and union territory master data
- `scholarship_categories`: joins scholarships to one or more eligible categories
- `scholarship_states`: joins scholarships to one or more eligible states
- `bookmarks`: stores student bookmarks without requiring login by using a browser session key
- `news`: stores scholarship news and update articles for the portal
- `trending_scholarships`: cached trending scores for fast homepage and analytics queries
- `notifications`: portal-wide reminders and notices
- `contact_messages`: messages from the public contact form
- `faqs`: admin-managed frequently asked questions
- `activity_logs`: audit trail of sensitive admin actions

## ER Diagram Description

- One `admin` can create many `news` records
- One `admin` can create many `notifications`
- One `admin` can create many `faq` entries
- One `admin` can resolve many `contact_messages`
- One `admin` can generate many `activity_logs`
- One `scholarship` can have many `bookmarks`
- One `scholarship` can have many related `news` items
- One `scholarship` can have many `notifications`
- One `scholarship` has zero or one `trending_scholarships` entry
- One `scholarship` can map to many `categories` through `scholarship_categories`
- One `category` can map to many `scholarships` through `scholarship_categories`
- One `scholarship` can map to many `states` through `scholarship_states`
- One `state` can map to many `scholarships` through `scholarship_states`

## Schema Highlights

### Scholarships

The scholarship table stores provider data, eligibility thresholds, links, dates, status, score-related fields, and descriptive content. Search-heavy columns such as name, type, gender, degree, branch, year, and deadline are indexed.

### Categories and States

These are lookup tables. They prevent duplicated text values and keep filtering consistent.

### Join Tables

`scholarship_categories` and `scholarship_states` keep the schema normalized and support scholarships that apply to multiple categories or states.

### Bookmarks

Because students do not log in, bookmarks are linked to a `browser_session_key` instead of a user table. A unique constraint prevents duplicate bookmarks for the same session and scholarship.

### Trending

Trending is stored separately because it is computed data, not source data. This allows scheduled recalculation later without bloating the core scholarship table.

### Activity Logs

Audit data is stored independently so operational logging does not pollute the admin or scholarship tables.

## Index Strategy

- Lookup indexes on `email`, `slug`, `code`, and foreign keys
- Search indexes on scholarship type, name, deadline, income, CGPA, degree, branch, and year
- Composite indexes for common admin and analytics queries
- Unique constraints on join-table pairs to prevent duplicate mappings

## Real-World Improvement Path

- Add Alembic migrations before production deployment
- Move large text search to PostgreSQL full-text search if data grows significantly
- Add soft-delete columns for content moderation workflows
- Partition or archive audit logs if admin activity becomes very high
