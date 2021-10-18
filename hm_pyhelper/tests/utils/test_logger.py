from unittest import TestCase
from hm_pyhelper.utils.logger import get_logger, _log_format
import re
import logging


class TestExample(TestCase):
    def test_logging(self):
        logger = get_logger(__name__)

        with self.assertLogs() as captured:
            logger.debug("Hello world.")

        # check that there is only one log message
        self.assertEqual(len(captured.records), 1)
        record = captured.records[0]
        formatter = logging.Formatter(_log_format)
        formatted_output = formatter.format(record)

        # Do not check timestamp and filepath because those change
        # based on the environment and run time
        expected_partial_output_regex = re.escape(
            " - [DEBUG] - test_logger - (test_logger.py).test_logging -- ")
        expected_output_regex = ".*" + \
            expected_partial_output_regex + ".*" + \
            " - Hello world."
        are_logs_correct = re.search(expected_output_regex, formatted_output)
        self.assertTrue(are_logs_correct)

    def test_custom_log_format(self):
        log_string = f"[%(levelname)s] - %(name)s: %(message)s"  # noqa: F541 E501
        log_message = "test log string"
        logger = get_logger(__name__, log_string)

        with self.assertLogs() as captured:
            logger.info(log_message)

        # check that there is only one log message
        self.assertEqual(len(captured.records), 1)
        record = captured.records[0]
        formatter = logging.Formatter(log_string)
        formatted_output = formatter.format(record)

        result = re.match("\\[INFO\\]\\s-\\s.*:\\s" + log_message,
                          formatted_output)
        self.assertTrue(result)
