###################################
#  metering/tests/test_dashboard.py
###################################

from django.test import TestCase
from django.core.management import call_command
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


class DashboardAuthTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_dashboard_requires_auth(self):
        resp = self.client.get("/api/dashboard/me/")
        self.assertIn(resp.status_code, (401, 403))

    def test_dashboard_returns_data_when_authenticated(self):
        call_command("seed_dev")
        user = User.objects.get(username="testuser")
        self.client.force_authenticate(user=user)

        resp = self.client.get("/api/dashboard/me/")
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(resp.data["rows"], 1)
