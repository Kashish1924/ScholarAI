# ScholarAI Module 4: Admin Backend

## Why This Module Matters

The student portal can only stay trustworthy if admins can manage scholarship data safely. Module 4 introduces protected admin workflows so only authorized administrators can create, update, and delete records.

## What Was Added

- Session-based admin login
- Protected admin route decorator
- Password hashing with Werkzeug
- Activity logging for login, logout, create, update, and delete events
- Admin dashboard summary service
- Admin scholarship management screens
- Interactive admin seed script

## How It Works

- Admins sign in using a validated Flask-WTF form
- Passwords are checked against hashed values stored in the database
- Successful login stores the admin id in the Flask session
- Protected routes require an authenticated session
- Important admin actions are stored in `activity_logs`

## Security Notes

- Passwords are never stored in plain text
- CSRF protection remains active for admin forms
- Admin routes are guarded with a reusable decorator
- Login failures do not reveal whether the email or password was wrong
- Admin actions are auditable through activity logs

## Common Mistakes This Avoids

- Storing passwords directly in the database
- Repeating login checks in every route
- Mixing admin auth logic into student-facing modules
- Allowing destructive admin actions without audit trails

## Interview Talking Points

- Why sessions instead of tokens for admin web pages: sessions fit server-rendered dashboards well
- Why hash passwords: plain-text passwords are a severe security risk
- Why log admin actions: sensitive management operations should be traceable
- Why keep auth and management services separate: it improves maintainability and testing
