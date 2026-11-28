#!/usr/bin/env python3
"""Deterministic production monitor tests; no live URLs are contacted."""
from __future__ import annotations

import unittest
import urllib.error
from email.message import Message
from unittest.mock import Mock, patch

import check_production_seo as monitor


class FakeResponse:
    status = 200
    headers = {"Content-Type": "text/html; charset=utf-8", "X-Robots-Tag": ""}

    def __init__(self, url: str):
        self.url = url

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, limit):
        return b"ok"

    def geturl(self):
        return self.url


class ProductionMonitorTests(unittest.TestCase):
    def setUp(self):
        monitor._CACHE.clear()

    def test_inventory_is_derived_from_project_catalog_and_contains_both_locales(self):
        routes = monitor.expected_routes()
        self.assertEqual(len(routes), 22)
        self.assertIn("/en/", routes)
        self.assertNotIn("/", routes)
        self.assertIn("/id/", routes)
        self.assertIn("/en/projects/holy-smart/", routes)
        self.assertNotIn("/projects/holy-smart/", routes)
        self.assertIn("/id/projects/ktadbrnr/", routes)

    def test_http_failure_classes_preserve_transient_and_bot_protection_states(self):
        self.assertEqual(monitor.classify_http(404), "PERMANENT_HTTP_FAILURE")
        self.assertEqual(monitor.classify_http(429), "RATE_LIMITED")
        self.assertEqual(monitor.classify_http(500), "SERVER_ERROR")
        self.assertEqual(monitor.classify_http(999), "BOT_PROTECTION")

    def test_redirect_tracker_counts_a_long_chain(self):
        tracker = monitor.RedirectTracker()
        request = monitor.urllib.request.Request("https://mydv.my.id/")
        headers = Message()
        for index in range(4):
            request = tracker.redirect_request(request, None, 302, "Found", headers, f"https://mydv.my.id/step-{index}/")
        self.assertEqual(len(tracker.chain), 4)

    @patch.object(monitor.time, "sleep")
    @patch.object(monitor.urllib.request, "build_opener")
    def test_rate_limit_retries_and_recovers(self, build_opener, _sleep):
        response = FakeResponse("https://mydv.my.id/")
        opener = Mock()
        opener.open.side_effect = [urllib.error.HTTPError("https://mydv.my.id/", 429, "limited", Message(), None), response]
        build_opener.return_value = opener
        self.assertEqual(monitor.fetch("https://mydv.my.id/")[0], 200)
        self.assertEqual(opener.open.call_count, 2)

    @patch.object(monitor.time, "sleep")
    @patch.object(monitor.urllib.request, "build_opener")
    def test_not_found_is_classified_without_retry(self, build_opener, _sleep):
        opener = Mock()
        opener.open.side_effect = urllib.error.HTTPError("https://mydv.my.id/missing/", 404, "missing", Message(), None)
        build_opener.return_value = opener
        result = monitor.fetch("https://mydv.my.id/missing/")
        self.assertEqual(result[0], 404)
        self.assertEqual(opener.open.call_count, 1)

    @patch.object(monitor.time, "sleep")
    @patch.object(monitor.urllib.request, "build_opener")
    def test_server_error_retries_then_remains_visible(self, build_opener, _sleep):
        opener = Mock()
        opener.open.side_effect = urllib.error.HTTPError("https://mydv.my.id/", 500, "server error", Message(), None)
        build_opener.return_value = opener
        result = monitor.fetch("https://mydv.my.id/server-error/")
        self.assertEqual(result[0], 500)
        self.assertEqual(opener.open.call_count, monitor.RETRIES + 1)

    @patch.object(monitor.time, "sleep")
    @patch.object(monitor.urllib.request, "build_opener")
    def test_timeout_uses_bounded_retries_then_raises(self, build_opener, _sleep):
        opener = Mock()
        opener.open.side_effect = TimeoutError("slow")
        build_opener.return_value = opener
        with self.assertRaises(TimeoutError):
            monitor.fetch("https://mydv.my.id/slow/")
        self.assertEqual(opener.open.call_count, monitor.RETRIES + 1)


if __name__ == "__main__":
    unittest.main()
