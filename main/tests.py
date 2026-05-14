from django.contrib.auth.models import AnonymousUser
from django.db import DatabaseError
from django.test import RequestFactory, TestCase
from django.urls import NoReverseMatch, URLPattern, URLResolver, get_resolver, reverse
from itertools import combinations
from unittest.mock import patch

from . import views


def _iter_named_patterns(patterns=None, namespaces=None, parent_kwargs=None):
    patterns = patterns or get_resolver().url_patterns
    namespaces = namespaces or []
    parent_kwargs = parent_kwargs or {}
    for pattern in patterns:
        if isinstance(pattern, URLResolver):
            next_namespaces = namespaces
            if pattern.namespace:
                next_namespaces = [*namespaces, pattern.namespace]
            next_kwargs = {**parent_kwargs, **_generated_kwargs(pattern)}
            yield from _iter_named_patterns(
                pattern.url_patterns,
                next_namespaces,
                next_kwargs,
            )
        elif isinstance(pattern, URLPattern) and pattern.name:
            name = ":".join([*namespaces, pattern.name])
            yield name, pattern, parent_kwargs


def _sample_value(converter):
    if converter.__class__.__name__ == "IntConverter":
        return 1
    if converter.__class__.__name__ == "UUIDConverter":
        return "00000000-0000-0000-0000-000000000001"
    if converter.__class__.__name__ == "PathConverter":
        return "sample/path"
    return "sample-slug"


def _sample_value_for_kwarg(name):
    if name.endswith("_pk") or name.endswith("_id") or name == "pk":
        return 1
    if name == "format":
        return "json"
    return "sample-slug"


def _generated_kwargs(pattern):
    if pattern.pattern.converters:
        return {
            key: _sample_value(converter)
            for key, converter in pattern.pattern.converters.items()
        }
    regex = getattr(pattern.pattern, "regex", None)
    if not regex:
        return {}
    return {
        key: _sample_value_for_kwarg(key)
        for key in regex.groupindex
        if key != "format"
    }


def _route_kwargs_candidates(parent_kwargs, pattern_kwargs):
    combined = {**parent_kwargs, **pattern_kwargs}
    candidates = [combined]

    outer_scope_keys = (
        "facility_slug",
        "faction_slug",
        "organization_slug",
        "facility_enrollment_slug",
    )
    removable_keys = [
        key for key in outer_scope_keys if key in combined and key not in pattern_kwargs
    ]
    for count in range(1, len(removable_keys) + 1):
        for keys_to_remove in combinations(removable_keys, count):
            scoped_variant = {
                key: value
                for key, value in combined.items()
                if key not in keys_to_remove
            }
            if scoped_variant not in candidates:
                candidates.append(scoped_variant)

    if pattern_kwargs and pattern_kwargs not in candidates:
        candidates.append(pattern_kwargs)

    if parent_kwargs and parent_kwargs not in candidates:
        candidates.append(parent_kwargs)

    return candidates


class MainViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_healthcheck_returns_ok(self):
        response = self.client.get(reverse("healthcheck"))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["database"], "ok")
        self.assertIn("timestamp", payload)

    def test_healthcheck_reports_database_errors(self):
        with patch("main.views.connection.ensure_connection") as mocked:
            mocked.side_effect = DatabaseError("unavailable")
            response = self.client.get(reverse("healthcheck"))
        self.assertEqual(response.status_code, 503)
        payload = response.json()
        self.assertEqual(payload["database"], "error")

    def test_home_view_returns_response(self):
        request = self.factory.get("/dashboard/")
        request.user = AnonymousUser()
        request.session = {}
        response = views.home(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Quick access")
        self.assertContains(response, "Camp coordination, ready for today.")


class NamedRouteIntegrityTests(TestCase):
    skipped_namespaces = {"admin", "api-auth"}
    skipped_route_names = {"api-root"}

    def test_named_routes_reverse_with_generated_kwargs(self):
        failures = []
        checked = 0

        for route_name, pattern, parent_kwargs in _iter_named_patterns():
            namespace = route_name.split(":", 1)[0]
            if namespace in self.skipped_namespaces or route_name in self.skipped_route_names:
                continue

            pattern_kwargs = _generated_kwargs(pattern)
            errors = []
            for kwargs in _route_kwargs_candidates(parent_kwargs, pattern_kwargs):
                try:
                    reverse(route_name, kwargs=kwargs or None)
                except NoReverseMatch as exc:
                    errors.append(f"{kwargs}: {exc}")
                    continue
                except Exception as exc:
                    failures.append(f"{route_name} kwargs={kwargs}: {exc}")
                    break
                checked += 1
                break
            else:
                failures.append(f"{route_name}: {' | '.join(errors)}")

        self.assertGreater(checked, 25)
        self.assertEqual(failures, [])
