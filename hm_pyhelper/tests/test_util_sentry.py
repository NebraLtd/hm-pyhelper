from logging import LogRecord
from unittest import TestCase
import hm_pyhelper.util.sentry as sentry_util
import json
import os

TESTDATA_DIR = os.path.join(os.path.dirname(__file__), "data/sentry")


class TestSentryUtil(TestCase):

    def setUp(self) -> None:
        error_logging_event_filename = os.path.join(TESTDATA_DIR, "sample_logging_event.json")
        exception_event_filename = os.path.join(TESTDATA_DIR, "sample_exception_event.json")
        logging_hints_filename = os.path.join(TESTDATA_DIR, "sample_logging_hints.json")
        self.error_logging_event = json.load(open(error_logging_event_filename, "r"))
        self.exception_event = json.load(open(exception_event_filename, "r"))
        self.logging_hints = json.load(open(logging_hints_filename, "r"))
        self.logging_hints['log_record'] = LogRecord(name='error log', level=3,
                                                     pathname='./test_file.py',
                                                     lineno=93, msg='error',
                                                     args={}, exc_info=None)

    def test_exception_event(self):
        # reset accumulated counters at start of test.
        sentry_util.event_counters = {}
        ret_value = sentry_util.before_send_filter(self.exception_event, {})
        self.assertIs(ret_value, self.exception_event)
        self.assertEqual(len(sentry_util.event_counters), 0)

    def test_error_without_hints(self):
        sentry_util.event_counters = {}
        ret_value = sentry_util.before_send_filter(self.error_logging_event, None)
        self.assertIs(ret_value, self.error_logging_event)
        self.assertEqual(len(sentry_util.event_counters), 0)

    def test_error_with_empty_hints(self):
        sentry_util.event_counters = {}
        ret_value = sentry_util.before_send_filter(self.error_logging_event, {})
        self.assertIs(ret_value, self.error_logging_event)
        self.assertEqual(len(sentry_util.event_counters), 0)

    def test_error_with_hints(self):
        sentry_util.event_counters = {}
        for count in range(1, 256):
            ret_value = sentry_util.before_send_filter(self.error_logging_event, self.logging_hints)
            if count in [1, 2, 4, 8, 16, 32, 64, 128, 256]:
                self.assertIs(ret_value['extra'][sentry_util.EVENT_COUNT_KEY], count)
            else:
                self.assertEqual(ret_value, None)
