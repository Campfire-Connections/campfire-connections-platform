# Campfire Connections

A unified platform for councils, camps, and training centers to run seasons, sessions, and people on a single screen. Campfire Connections blends scheduling, housing, classes, and communication across every role—admins, facilities, factions, faculty, leaders, and attendees.

## What you can do

- **Plan seasons without spreadsheets**: Stand up organizations, facilities, sessions, weeks, and periods; track capacities for cabins, tents, and classes.
- **Keep everyone in the right place**: Match factions to weeks/quarters, then slot attendees, leaders, and faculty with automatic availability and overbooking protection.
- **Give each role its own portal**: Leaders see faction rosters, faculty see assignments, attendees see personal schedules. Navigation is dynamic and pin-able for quick access.
- **See the day at a glance**: Dashboard widgets surface rosters, schedules, metrics, and resources per portal; layouts and favorites are saved per user.
- **Report with confidence**: Build and download snapshots; permissions ensure the right people see the right data.

## Who it's for

- Councils and districts coordinating multi-week programming.
- Facility teams juggling cabins/quarters and rotating instructors.
- Faction/crew leaders tracking their people and classes.
- Training teams running repeatable courses with rosters and requirements.

## Highlights

- **Scheduling Service**: One source of truth that enforces capacity across quarters and class rosters, no matter which form or API updates the data.
- **Dynamic Navigation**: Registry-driven menu with quick favorites you can pin/unpin right from the navbar.
- **Role-Based Dashboards**: Widget registry per portal; users can hide/show/reorder cards and keep preferences.
- **Safe Defaults**: Profile creation, slugging, and label setup are automated; activation emails are sent asynchronously.

## Quick start (demo friendly)

### Docker

```bash
docker compose build
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py seed_test_data
docker compose up
```

Open `http://localhost:8000/`.

### Local Python

```bash
python3 -m venv .venv
source .venv/bin/activate
./install_local.sh          # editable installs, no network needed
python manage.py migrate
python manage.py seed_test_data
python manage.py runserver
```

Demo accounts (password `testpass123`):
- `campfire.admin` (admin)
- `donna.faculty`, `mason.faculty` (faculty)
- `leo.leader`, `sara.leader` (leaders)
- `amy.attendee`, `riley.attendee` (attendees)

Sign in at `/login/`. The admin portal is available at `/accounts/admin-portal/`.

## Apps in the suite

- **Core**: shared mixins, dashboards, navigation, portal registry.
- **Organization**: councils/districts and labels.
- **Facility**: facilities, departments, quarters, faculty profiles.
- **Faction**: factions, leaders, attendees.
- **Course & Enrollment**: courses, facility classes, seasons/sessions, availability-aware enrollments.
- **Reports**: templates and generated output.
- **Pages/Main/User**: landing pages, auth, dynamic nav favorites, activation flows.

## Deploy notes

- Settings are modular (`campfire_connections/settings/base.py` with `local.py` defaulted in manage.py and `prod.py` for WSGI/ASGI); override via `DJANGO_SETTINGS_MODULE` as needed.
- Activation links use `SITE_BASE_URL`/`ALLOWED_HOSTS`; mail is fire-and-forget, suitable for background workers later.
- Everything is Django 5.2.x; tests run with `python manage.py test`.

## Configuration & static/media

- Copy `.env.example` to `.env` and export it (`set -a; source .env; set +a`) or set env vars in your process manager. Use strong values for `DJANGO_SECRET_KEY`, disable `DJANGO_DEBUG`, and set `DJANGO_ALLOWED_HOSTS` for production.
- Static assets are served from `pages/static` in development; run `python manage.py collectstatic` for deploys (outputs to `staticfiles`). Point your web server or CDN there.
- User uploads live under `media/`; ensure your web server or storage backend serves `MEDIA_URL` safely.
- Security flags (`DJANGO_SESSION_COOKIE_SECURE`, `DJANGO_CSRF_COOKIE_SECURE`, `DJANGO_SECURE_*`) default off locally—enable them in production.

## Tooling

- Formatting/linting config lives in `pyproject.toml` (black, isort, ruff, mypy).
- `make test` runs the Django suite through `.venv/bin/python`.
- `docker compose exec web python manage.py check` validates the running container.

## Frontend conventions

- App pages should extend the shared templates in `pages/templates/base/`.
- List pages should use `base/list.html`; form pages should use `base/form.html`; detail pages should use `base/show.html` unless a page has a specific dashboard layout.
- Use theme tokens from `pages/static/css/layout.css` (`--card`, `--panel`, `--text`, `--muted`, `--border`, `--accent`) instead of hardcoded light colors.
- Prefer `content-card`, Bootstrap buttons, and the `page_actions` block for top-level actions so dark mode and mobile layouts stay consistent.
