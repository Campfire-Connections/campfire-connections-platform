# Campfire Connections Platform

A modular, multi-portal Django platform for managing organizations, facilities, factions, courses, enrollments, reports, and user portals (faculty, leader, attendee). This project stitches together the Campfire-Connections repos into a single cohesive Django site.

## Architecture Overview

- `campfire_connections/` – main Django project (settings, URLs).
- `main/` – simple landing/dashboard app.
- Root-level directories (`core`, `organization`, `facility`, `faction`, `course`, `enrollment`, `reports`, `pages`, `user`) hold each domain app that is pip-installed in editable mode.

Key domain relationships:
- **Organization** → hierarchical parent/child structure (can contain facilities and factions).
- **Facility** → belongs to an organization; manages departments, quarters, faculty.
- **Faction** → belongs to an organization; manages leaders and attendees.
- **User / Profiles** → a single custom `User` model with role-specific OneToOne profiles (`FacultyProfile`, `LeaderProfile`, `AttendeeProfile`).
- **Enrollment** → orchestrates facility/faction/course scheduling via dedicated models and tables.

## Recent Enhancements

- Added `HierarchicalEntity` and `AddressableMixin` in `core/mixins/models.py` so Organization, Facility, and Faction share the same set of mixins (name/slug/parent/address/audit).
- Flattened leader, attendee, and faculty models to operate purely through their profiles; removed old multi-table inheritance and standardized profile forms/tables/serializers around the shared `ProfileUserFieldsMixin`.
- Introduced scoped mixins (`OrgScopedMixin`, `FacilityScopedMixin`, `FactionScopedMixin`, `PortalPermissionMixin`) to automatically filter views by the active portal and enforce role-based access.
- Added database constraints to ensure slugs are unique per organization and that `(faction, user)` / `(facility, user)` combinations are unique.
- Created a portal registry (`core/portals.py`) describing each portal’s dashboard template, widgets, and allowed user types; dashboards now pick up templates/permissions based on `portal_key`.
- Refactored tables (leaders, attendees, faculty) to work directly with profile models instead of raw users.

## Development

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
./install_local.sh  # installs core/facility/etc via editable installs (no network needed)
python manage.py migrate
python manage.py createsuperuser  # optional admin
python manage.py runserver
```

### Seed Sample Data

Use the dedicated management command whenever you want a fully-linked demonstration dataset:

```bash
python manage.py seed_test_data
```

The command is idempotent, so re-running it refreshes the same objects without creating duplicates. It wires three organizations, two facilities (River Bend + Summit Ridge), departments, quarters, two factions, requirements/courses, organization + facility enrollments, weekly periods, facility classes, faction enrollments, and example faculty/leader/attendee enrollments. Sample accounts created with password `testpass123`:
- `campfire.admin` – Admin portal access.
- `donna.faculty` – River Bend faculty lead tied to Wilderness First Aid.
- `mason.faculty` – Summit Ridge faculty mentor for the leadership cohort.
- `leo.leader` / `sara.leader` – Faction leaders for Eagle Patrol + Aurora Crew.
- `amy.attendee` / `riley.attendee` – Attendees mapped to navigation and leadership programs.

### Portal Routing

`campfire_connections/urls.py` wires each domain app (pages, organization, facility, faction, course, enrollment, reports) and pulls in `main` plus Django's auth views. Landing page lives in `pages`, dashboards/routes in each app.

### Organization

- Models: `Organization`, `OrganizationLabels` in `organization/models/organization.py`.
- URLs: `organization/urls.py` handles CRUD views and DRF router.
- Views use the scoped mixins to ensure organization context is respected.

### Facility

- Models: `Facility`, `Department`, `Quarters`, `FacultyProfile` (`facility/models`).
- Views: `facility/views/facility.py` uses `FacilityScopedMixin` and `PortalPermissionMixin`.
- Forms/Tables: `FacultyForm`, `FacultyTable` operate on `FacultyProfile`.
- URLs under `/facilities/` include nested routes for departments, quarters, faculty, classes, enrollments, courses.

### Faction

- Models: `Faction`, `LeaderProfile`, `AttendeeProfile` (`faction/models`).
- Views and tables use profile models and scoped mixins (`FactionScopedMixin`).
- Leader/Attendee forms share `ProfileUserFieldsMixin`; tables and DRF serializers operate on profiles.

### Courses & Enrollment

- `course/` – course catalog, facility classes, requirements.
- `enrollment/` – facility, faction, faculty, leader, attendee enrollments with extensive tables/forms/views.

### Reports & Pages

- `reports/` – user-defined report templates and generated reports.
- `pages/` – static/landing pages, widgets, dashboards, dynamic forms.

### Core Utilities

- `core/mixins/models.py` – base mixins for audit, slug, address, hierarchy, track changes.
- `core/mixins/views.py` – portal scoping, Ajax handling, permission mixins.
- `core/views/base.py` – base class for list/detail/create/update/manage/dashboard views.
- `core/portals.py` – registry of portal metadata (labels, templates, widgets, permissions).

### User App

- Custom `User` model in `user/models.py` with `UserType` choices and profile creation signals.
- Forms (`user/forms.py`) include `ProfileUserFieldsMixin` for shared user fields and registration form.
- Serializers (`user/serializers.py`) provide `UserSummarySerializer` and `BaseProfileSerializer` for nested JSON structures.
- Views include login/register/dashboard endpoints using the shared mixins.

### Running Tests / Lint

No dedicated test suite is included here, but you can run Django checks:
```bash
python manage.py check
```
Add new tests under each app’s `tests.py` as you extend functionality.

### Git Submodules vs Local Repos

Each Campfire-Connections module is a sibling directory at the repo root. Editable installs (`pip install -e ./core`, etc.) keep imports consistent while letting you work inside each module directly.

## Future Work

- Expand automated tests for scoped mixins, dashboards, and profile constraints.
- Flesh out the portal registry with widget classes and dynamic dashboards.
- Add developer docs for writing new portal widgets and wiring new modules.
