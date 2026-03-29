# CCS — Caro Care Schedule

A web app for people with ME/CFS to coordinate care and social contact.
Friends and caretakers can sign up to a shared schedule, keeping the load distributed and community alive.

---

## Tech Stack

| Layer    | Choice                                    |
| -------- | ----------------------------------------- |
| Backend  | Django (Python)                           |
| Database | PostgreSQL (production) / SQLite (dev)    |
| Email    | Brevo SMTP — free tier, 300 emails/day    |
| Frontend | Django templates (server-rendered)        |
| Hosting  | TBD                                       |

---

## Roles

| Role                  | Description                                                                        |
| --------------------- | ---------------------------------------------------------------------------------- |
| Admin                 | Full control: invite users, manage timeslots, post announcements, edit wiki, tasks |
| User                  | Can view schedule, respond to slots, suggest activities                            |
| Core Care Taker (CCT) | Same as User, plus access to the task view. Assigned by Admin                      |

Admins can grant admin rights to other users.
Admins can promote any User to CCT (Core Care Taker) to grant task view access.
---

## Minimal Functionality

### 1. Timeslot Management

**Admin creates a timeslot and proposes it to one or more users.**

A timeslot has:

- Start and end time
- Activity type (e.g. phone call, walk, errand)
- Medium: phone / video call / in person
- Location (optional, for in-person)
- Proposed to: one user or all users

The invited user responds with one of:

- **A — Accept**
- **B — Pending** (no response yet)
- **C — Decline**
- **D — Suggest alternative slot** (user proposes a different time)

If email notifications are enabled for that user, they receive an email on each status change.

**Conflict rule:** If two timeslots overlap, both are flagged with a warning. The admin decides how to resolve the conflict (keep both, cancel one, reschedule).

---

### 2. User-Suggested Activities

Users can suggest an activity to the admin. The admin then decides:

- **A — Accept** (and create a timeslot for it)
- **B — Pending**
- **C — Decline**
- **D — Propose alternative slot**

The user receives a notification when the admin responds.

Each user has a recommended maximum slot duration visible during suggestion.
This value is set globally by the admin and can be adjusted per user.

---

### 3. Announcements

Admins can post announcements visible on a dedicated dashboard.

Each announcement:

- Has a title, body text, and a creation date
- Can be set as active or inactive (expired announcements are hidden)
- Has an optional expiry date
- Can trigger an email to all users with email notifications enabled

---

### 4. Wiki (Link Collection)

Admins can share helpful links (e.g. ME/CFS resources, support organisations).

Each wiki entry has:

- A title
- A URL
- Author and creation date
- Cluster_name

---

### 5. Invitation Flow

1. Admin enters a user's name and email and sends an invite.
2. Django generates a unique invite token and emails a registration link to the user.
3. The user opens the link, sets their password, and activates their account.
4. If the invite token expires before registration, the admin is notified and can re-send the invite.
5. Users log in with email + password thereafter.

Password reset ("forgot password") is handled by Django's built-in auth views.

---

ored_in


### 6. Email / Notification System

#### Service: Brevo (formerly Sendinblue)

- Free tier: 300 emails/day, unlimited contacts, no credit card required.
- Sign up at brevo.com → get SMTP credentials (host, port, login, API key as password).

#### How it works in Django

Django has a built-in email system. You configure it once in `settings.py` and then call
`send_mail(...)` or `send_mass_mail(...)` anywhere in the code.

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-relay.brevo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-brevo-login@example.com'
EMAIL_HOST_PASSWORD = 'your-brevo-smtp-api-key'   # from Brevo SMTP settings
DEFAULT_FROM_EMAIL = 'ccs@yourdomain.com'
```

**Never put credentials in code.** Use environment variables via a `.env` file
and the `django-environ` or `python-decouple` package:

```python
# settings.py — safe version
import environ
env = environ.Env()
environ.Env.read_env()

EMAIL_HOST_PASSWORD = env('BREVO_SMTP_KEY')
```

**During development**, swap to the console backend so no real emails are sent:

```python
# settings.py (dev only)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

#### What to watch out for

| Issue                        | What to do                                                                     |
| ---------------------------- | ------------------------------------------------------------------------------ |
| Emails land in spam          | Set up SPF and DKIM DNS records on your domain (Brevo guides you through this) |
| Credentials in git           | Always use `.env` + add `.env` to `.gitignore` before first commit             |
| Email sending blocks request | Fine for a small app; move to Celery later if it becomes slow                  |
| 300/day limit hit            | Very unlikely at this scale; upgrade to next Brevo tier if needed              |

Emails are sent synchronously (during the HTTP request), which is simple and sufficient for this app size.
If the send fails, Django raises an exception — catch it and show the admin a warning rather than letting the page crash.

---

### Task Management
The role CCT is asigned by the admin for the user only CCTs can see the task view.

The task view includes task description some necessary information and a point to the server where stuff inptut/output is stored. plus status of task and which of the CCTs does the task

Task can be initiated by Admin OR CCT and CCT and Admin CAN be informed (if choosen in settings) if the status of a task changes

## Data Model

### User

| Field               | Type                    | Notes                     |
| ------------------- | ----------------------- | ------------------------- |
| id                  | int (PK)                |                           |
| name                | string                  |                           |
| email               | string (unique)         | used for login            |
| password            | hashed                  | Django handles this       |
| role                | enum                    | Admin, User               |
| status              | enum                    | invited, active, disabled |
| invite_token        | string (nullable)       |                           |
| invite_expires_at   | datetime (nullable)     |                           |
| email_notifications | bool                    | default true              |
| max_slot_duration   | int (minutes, nullable) | overrides global default  |
| created_at          | datetime                |                           |

### Timeslot

| Field        | Type              | Notes                       |
| ------------ | ----------------- | --------------------------- |
| id           | int (PK)          |                             |
| start        | datetime          |                             |
| end          | datetime          |                             |
| location     | string (nullable) |                             |
| medium       | enum              | phone, video, in_person     |
| created_by   | FK → User         | admin or user who initiated |
| created_at   | datetime          |                             |
| has_conflict | bool              | set by conflict detection   |

### Activity

| Field            | Type                     | Notes                                    |
| ---------------- | ------------------------ | ---------------------------------------- |
| id               | int (PK)                 |                                          |
| name             | string                   |                                          |
| timeslot         | FK → Timeslot            |                                          |
| proposed_to      | FK → User                | which user this is for                   |
| user_status      | enum                     | pending, accepted, declined, alternative |
| admin_status     | enum                     | pending, accepted, declined, alternative |
| alternative_slot | FK → Timeslot (nullable) | if D chosen                              |
| created_by       | FK → User                |                                          |
| created_at       | datetime                 |                                          |

### Announcement

| Field      | Type                | Notes                   |
| ---------- | ------------------- | ----------------------- |
| id         | int (PK)            |                         |
| title      | string              |                         |
| text       | text                |                         |
| author     | FK → User           |                         |
| send_mail  | bool                | trigger email on save   |
| expires_at | datetime (nullable) |                         |
| is_active  | bool                |                         |
| created_at | datetime            |                         |


### Task

id
title
text
author
status 
priority
worker
stored_in

### WikiEntry

| Field      | Type      | Notes |
| ---------- | --------- | ----- |
| id         | int (PK)  |       |
| title      | string    |       |
| url        | string    |       |
| author     | FK → User |       |
| created_at | datetime  |       |

---

## Design Guidelines

- Dark theme with soft, low-contrast colors (no harsh whites or bright accents)
- Calm, readable font — large enough to read when fatigued
- Minimal interface: one clear action per screen, no clutter
- Mobile-first layout (users may be lying down, using a phone)
- Minimal clicks to complete any action
- No auto-playing content, no flashing elements
