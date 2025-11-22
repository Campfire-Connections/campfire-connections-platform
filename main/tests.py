from django.contrib.auth.models import AnonymousUser
from django.db import DatabaseError
from django.test import RequestFactory, TestCase
from django.urls import reverse
from unittest.mock import patch

from . import views


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
