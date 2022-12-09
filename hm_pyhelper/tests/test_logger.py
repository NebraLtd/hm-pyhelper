from unittest import TestCase
from hm_pyhelper.logger import get_logger, _log_format
import re
import logging


class TestLogger(TestCase):
    def test_get_logger(self):
        logger = get_logger(__name__)

        with self.assertLogs() as captured:
            logger.info("Hello world.")

        # check that there is only one log message
        self.assertEqual(len(captured.records), 1)
        record = captured.records[0]
        formatter = logging.Formatter(_log_format)
        formatted_output = formatter.format(record)

        # Do not check timestamp and filepath because those change
        # based on the environment and run time
        expected_partial_output_regex = re.escape(
            " - [INFO] - hm_pyhelper.tests.test_logger -" +
            " (test_logger.py).test_get_logger -- ")
        expected_output_regex = ".*" + \
            expected_partial_output_regex + ".*" + \
            " - Hello world."
        are_logs_correct = re.search(expected_output_regex, formatted_output)
        self.assertTrue(are_logs_correct)
