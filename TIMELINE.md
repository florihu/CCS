# CCS — Development Timeline

**Pace:** 3 hours/week · biweekly sprints (6 hours each)
**Total estimated effort:** ~120 hours → ~40 weeks (~10 months)

> Estimates assume you are learning Django and SQL as you go.
> Each sprint builds directly on the previous one — do not skip ahead.

---

## Skills You Need First

Before writing a single line of app code, work through these in order.
Each tutorial/resource is free.

### Python (if rusty)

- **Tutorial:** [Python.org official tutorial](https://docs.python.org/3/tutorial/) — chapters 1–9
- **What to focus on:** functions, classes, lists/dicts, error handling
- **Skip:** advanced chapters (iterators, generators) — not needed yet

### Django

- **Tutorial:** [Django official tutorial (Parts 1–7)](https://docs.djangoproject.com/en/stable/intro/tutorial01/)
  - Part 1–2: project setup, models, database
  - Part 3–4: views, templates, forms
  - Part 5: testing basics
  - Part 6–7: static files, admin panel
- **What you get:** the Django admin panel alone covers ~30% of this app for free

### SQL / Databases

- **Tutorial:** [SQLite Tutorial](https://www.sqlitetutorial.net/) — first 6 sections
- **What to focus on:** SELECT, INSERT, UPDATE, JOIN — but Django's ORM writes most SQL for you
- **Key insight:** you define models in Python, Django creates the database tables automatically

### HTML + CSS (just enough)

- **Tutorial:** [MDN HTML basics](https://developer.mozilla.org/en-US/docs/Learn/HTML/Introduction_to_HTML) + [CSS basics](https://developer.mozilla.org/en-US/docs/Learn/CSS/First_steps)
- **What to focus on:** forms, links, basic layout — Django templates handle the rest

### Git (version control — essential)

- **Tutorial:** [git - the simple guide](https://rogerdudler.github.io/git-guide/)
- **Do this on day one** — commit your work after every sprint

---

## Work Packages Overview

| # | Package                    | Hours | Sprints |
| - | -------------------------- | ----- | ------- |
| 1 | Environment Setup          | 6     | 1       |
| 2 | Django & SQL Learning      | 18    | 3       |
| 3 | Database Models            | 6     | 1       |
| 4 | User Auth & Login          | 6     | 1       |
| 5 | Invitation System          | 12    | 2       |
| 6 | Email Setup (Brevo)        | 6     | 1       |
| 7 | Timeslot CRUD              | 12    | 2       |
| 8 | Activity Workflow          | 12    | 2       |
| 9 | Conflict Detection         | 6     | 1       |
| 10 | Announcements             | 6     | 1       |
| 11 | Wiki                      | 6     | 1       |
| 12 | Frontend & Design         | 12    | 2       |
| 13 | Integration Testing       | 12    | 2       |
|   | **Total**                 | **120** | **20** |

---

## Sprint Schedule

### Sprint 1 — Environment Setup (Weeks 1–2)

**Goal:** Working Django project on your machine, committed to git.

Tasks:

- Install Python, pip, virtualenv
- Install Django: `pip install django`
- Create project: `django-admin startproject ccs`
- Run the dev server, see the welcome page
- Create a git repository, make your first commit

Skills needed: Python basics, command line, git intro

Deliverable: `http://localhost:8000` shows Django welcome page

---

### Sprint 2–4 — Django & SQL Learning (Weeks 3–8)

**Goal:** Complete the official Django tutorial (Parts 1–7). Do not skip.

Sprint 2 (Weeks 3–4): Tutorial Parts 1–2 — models, migrations, Django admin

Sprint 3 (Weeks 5–6): Tutorial Parts 3–4 — views, URL routing, templates, forms

Sprint 4 (Weeks 7–8): Tutorial Parts 5–7 — testing, static files, admin customisation

Skills needed: Django ORM, HTML templates, Django forms

> **Tip:** The tutorial builds a polls app. Your CCS app uses the same patterns — just different data.

---

### Sprint 5 — Database Models (Weeks 9–10)

**Goal:** All CCS models defined, database tables created, visible in Django admin.

Tasks:

- Create a `schedule` Django app inside the project
- Define models: `User` (extend Django's built-in), `Timeslot`, `Activity`, `Announcement`, `WikiEntry`
- Run `makemigrations` + `migrate`
- Register all models in `admin.py` — you can now create/edit records via the admin panel

Skills needed: Django models, migrations, model relationships (ForeignKey)

Deliverable: All five tables exist in the database; records creatable via `/admin`

---

### Sprint 6 — User Auth & Login (Weeks 11–12)

**Goal:** Users can log in and log out with email + password.

Tasks:

- Extend Django's `AbstractUser` with `role`, `status`, `email_notifications`, `max_slot_duration`
- Set `AUTH_USER_MODEL = 'schedule.User'` in settings (must be done before first migration)
- Configure login/logout URLs using Django's built-in `django.contrib.auth.views`
- Create a basic login page template
- Protect all other pages with `@login_required`

Skills needed: Django auth system, Django's `AbstractUser`

Deliverable: Login page at `/login`, redirect to dashboard after login

---

### Sprint 7–8 — Invitation System (Weeks 13–16)

**Goal:** Admin can invite users by email; user completes registration via link.

Sprint 7 (Weeks 13–14):

- Admin form: enter name + email, generate a `uuid` invite token, set expiry (7 days)
- Store `invite_token` + `invite_expires_at` on the User record
- Send invite email with a registration link containing the token (uses Brevo — see Sprint 9)

Sprint 8 (Weeks 15–16):

- Registration view: validate token, check expiry, let user set password
- On success: set `status = active`, clear token
- Expired token: show error, notify admin (flag in admin panel or email)
- Password reset using Django's built-in `PasswordResetView`

Skills needed: Django forms, UUID generation, Django's email functions, URL parameters

Deliverable: Full invite → register → login flow working end-to-end

---

### Sprint 9 — Email Setup / Brevo (Weeks 17–18)

**Goal:** All email sending works through Brevo SMTP; credentials stored safely.

Tasks:

- Sign up at brevo.com, get SMTP credentials
- Install `django-environ`: `pip install django-environ`
- Create `.env` file, add it to `.gitignore` immediately
- Configure `EMAIL_*` settings in `settings.py` using env vars
- Test with Django's `send_mail()` from the Django shell
- Set up console email backend for local dev (no real emails sent during testing)
- Write a reusable `send_notification(user, subject, body)` helper function

Skills needed: Environment variables, Django email settings, SMTP basics

Deliverable: Invite emails actually arrive in a real inbox

---

### Sprint 10–11 — Timeslot CRUD (Weeks 19–22)

**Goal:** Admins can create, edit, cancel timeslots and propose them to users; users can respond.

Sprint 10 (Weeks 19–20):

- Admin views: create timeslot (form with start, end, medium, location, proposed_to)
- List view showing all upcoming timeslots
- Link Activity to Timeslot on creation

Sprint 11 (Weeks 21–22):

- User response view: A/B/C/D buttons on a timeslot detail page
- D (alternative): user picks a new time via a form, creates an `alternative_slot`
- Status changes trigger email notification if `user.email_notifications = True`

Skills needed: Django class-based views (or function views), Django forms, datetime handling

Deliverable: Admin creates a slot, user accepts/declines/proposes alternative, both get emails

---

### Sprint 12–13 — Activity Workflow (Weeks 23–26)

**Goal:** Users can suggest activities; admin reviews and responds.

Sprint 12 (Weeks 23–24):

- User form: suggest an activity (name, preferred medium, preferred time)
- Show recommended max slot duration from their user profile
- Activity created with `admin_status = pending`

Sprint 13 (Weeks 25–26):

- Admin review list: all pending activity suggestions
- Admin responds A/B/C/D — same pattern as timeslot responses
- User notified by email on admin response

Skills needed: Django model status fields, filtering querysets, form validation

Deliverable: Full user-suggests → admin-responds → user-notified flow

---

### Sprint 14 — Conflict Detection (Weeks 27–28)

**Goal:** Overlapping timeslots are automatically flagged.

Tasks:

- On timeslot save, query for existing slots where time ranges overlap for the same user
- If overlap found: set `has_conflict = True` on both slots
- Admin dashboard highlights conflicted slots with a visible warning
- No automatic blocking — admin resolves manually

Skills needed: Django ORM query filters (`Q` objects), `__lt` / `__gt` field lookups

Deliverable: Creating two overlapping slots shows a conflict warning in the admin view

---

### Sprint 15 — Announcements (Weeks 29–30)

**Goal:** Admins post announcements; users see them on a dashboard; optional email blast.

Tasks:

- Admin form: title, text, expiry date, `send_mail` checkbox
- On save with `send_mail = True`: send email to all users with `email_notifications = True`
- Announcement dashboard: shows all `is_active = True` and non-expired announcements
- Auto-hide expired announcements (filter by `expires_at < now`)

Skills needed: Django signals or `save()` override, queryset date filtering

Deliverable: Announcement posted, email received, dashboard updated

---

### Sprint 16 — Wiki (Weeks 31–32)

**Goal:** Admins can add/edit/delete links; all users can view them.

Tasks:

- Admin form: title + URL
- Wiki list page: all entries, sorted by creation date
- Basic URL validation (must start with `http`)
- Non-admins see the list but have no add/edit buttons

Skills needed: Django permissions (`user.is_staff` or role check), template conditionals

Deliverable: Wiki page live with working add/delete for admin

---

### Sprint 17–18 — Frontend & Design (Weeks 33–36)

**Goal:** All pages look consistent, mobile-friendly, and relaxing to use.

Sprint 17 (Weeks 33–34):

- Create a base template with navigation, dark background, font choice
- Apply consistently across all pages
- Mobile layout using CSS flexbox or a minimal CSS framework (e.g. [Pico CSS](https://picocss.com/) — zero JS, dark mode built in)

Sprint 18 (Weeks 35–36):

- Review every screen for click count — reduce where possible
- Check all pages on a phone screen
- Readable font size (minimum 16px), sufficient contrast
- Suppress all non-essential visual noise

Skills needed: HTML/CSS, Django template inheritance (`{% extends %}`, `{% block %}`)

Deliverable: All screens usable on a phone, visually consistent

---

### Sprint 19–20 — Integration Testing (Weeks 37–40)

**Goal:** Manually test all key user journeys end-to-end; fix bugs found.

Sprint 19 (Weeks 37–38) — test each flow:

- [ ] Admin invites user → user registers → logs in
- [ ] Invite token expires → admin notified → resend works
- [ ] Admin creates timeslot → user responds A/C/D → emails sent correctly
- [ ] User suggests activity → admin responds → user notified
- [ ] Two overlapping slots → conflict flag appears
- [ ] Announcement with email → all eligible users receive it
- [ ] Wiki: add, view, delete link

Sprint 20 (Weeks 39–40) — fix & polish:

- Fix any bugs found in Sprint 19
- Test all email flows with a real inbox (not console backend)
- Test on mobile
- Final review of all form validation (what happens with empty fields, bad URLs, etc.)

Skills needed: Manual testing discipline, reading Django error pages, using Django shell for debugging

Deliverable: App is stable and usable as a real tool

---

## After the Timeline

Once the above is complete, potential next steps (not in scope now):

- Deploy to a hosting provider (Railway, Render, or Heroku — all have free tiers)
- Add a calendar view for timeslots
- iCal export so slots appear in a phone calendar
- Recurring slot templates
