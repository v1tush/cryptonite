import os
import subprocess
import sys
from datetime import date
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import OperationalError
from django.test import (
    SimpleTestCase,
    TestCase,
    TransactionTestCase,
    override_settings,
)
from django.urls import reverse

from ciphers.constants import HINT_PRICE
from ciphers.models import Cipher, CipherDayHistory, CipherHelp
from cryptonite.config import validate_production_settings


class ProductionSettingsTests(SimpleTestCase):
    key = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

    def test_rejects_missing_weak_and_placeholder_keys(self):
        for key in ('', 'fake-key', 'a' * 100, 'django-insecure-' + self.key):
            with (
                self.subTest(key=key),
                self.assertRaises(ImproperlyConfigured),
            ):
                validate_production_settings(key, ['example.com'])

    def test_rejects_empty_wildcard_scheme_and_port_hosts(self):
        for hosts in (
            [],
            [''],
            ['*'],
            ['.example.com'],
            ['https://example.com'],
            ['example.com:443'],
        ):
            with (
                self.subTest(hosts=hosts),
                self.assertRaises(ImproperlyConfigured),
            ):
                validate_production_settings(self.key, hosts)

    def test_accepts_explicit_host_names_and_addresses(self):
        validate_production_settings(
            self.key, ['app.example.com', '127.0.0.1', '[::1]']
        )

    def test_manage_check_refuses_unsafe_production_environment(self):
        base_env = os.environ | {
            'DJANGO_SETTINGS_MODULE': 'cryptonite.settings',
            'DJANGO_DEBUG': 'False',
        }
        for key, host, expected in (
            ('fake-key', 'example.com', 'DJANGO_SECRET_KEY must be'),
            (self.key, '*', 'DJANGO_ALLOWED_HOSTS must list explicit hosts'),
        ):
            with self.subTest(host=host):
                result = subprocess.run(
                    [sys.executable, 'manage.py', 'check'],
                    cwd=Path(__file__).resolve().parents[1],
                    env=base_env
                    | {'DJANGO_SECRET_KEY': key, 'DJANGO_ALLOWED_HOSTS': host},
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stderr)


class OperationsTests(TestCase):
    def test_health_reports_database_availability(self):
        url = reverse('health')
        self.assertEqual(self.client.get(url).json(), {'status': 'ok'})
        with patch(
            'core.health.connection.cursor', side_effect=OperationalError
        ):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {'status': 'unavailable'})

    @override_settings(DEBUG=True)
    def test_demo_is_repeatable_without_resetting_balance(self):
        call_command('seed_demo', stdout=StringIO())
        users = get_user_model().objects
        self.assertEqual(users.get(username='demo_player').money, HINT_PRICE)
        users.filter(username='demo_player').update(money=0)
        call_command('seed_demo', stdout=StringIO())
        self.assertEqual(users.get(username='demo_player').money, 0)
        self.assertEqual(Cipher.objects.count(), 1)
        self.assertEqual(CipherHelp.objects.count(), 1)

    @override_settings(DEBUG=False)
    def test_demo_requires_debug_mode(self):
        with self.assertRaises(CommandError):
            call_command('seed_demo')


class DailyCipherSchedulerTests(TransactionTestCase):
    @override_settings(DEBUG=True)
    def test_scheduler_once_is_idempotent_and_preserves_history(self):
        call_command('seed_demo', stdout=StringIO())
        first, second = date(2026, 1, 1), date(2026, 1, 2)
        with patch('scheduler_jobs.timezone.localdate', return_value=first):
            call_command('run_scheduler', once=True)
            call_command('run_scheduler', once=True)
        self.assertEqual(CipherDayHistory.objects.count(), 1)
        with patch('scheduler_jobs.timezone.localdate', return_value=second):
            call_command('run_scheduler', once=True)
        self.assertEqual(
            list(CipherDayHistory.objects.values_list('date', flat=True)),
            [first, second],
        )
