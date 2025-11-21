# Main App

The `main` app is a lightweight wrapper that provides the root landing page and shared dashboard
redirects for the combined project. It is intentionally thin—most portal logic lives in the other
apps.

## Responsibilities

- Simple landing/home view rendered at `/`.
- Default dashboard redirect that sends authenticated users to their role-specific portal.
- Placeholder templates/styles for marketing copy or global announcements.

## Tests

```bash
python manage.py test main
```

Add view tests here if you expand the landing page or introduce additional routes.
