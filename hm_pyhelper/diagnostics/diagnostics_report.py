import json

# Name of key in diagnostics containing meta-information about
# the overall state of the miner.
DIAGNOSTICS_PASSED_KEY = 'diagnostics_passed'

# Name of key containing an array of all the diagnostics
# that are considered to be errors.
DIAGNOSTICS_ERRORS_KEY = 'errors'


class DiagnosticsReport(dict):

    KEYS_TO_CHECK_IN_MANUFACTUING = {
        'ECC', 'onboarding_key', 'eth_mac_address', 'wifi_mac_address',
        'public_key', 'bluetooth', 'VARIANT', 'FREQ', 'serial_number'
    }

    KEYS_TO_CHECK_IN_GATEWAY_TRANSACTION_PAYLOAD = {
        'address', 'fee', 'owner', 'payer', 'txn', 'staking fee'
    }

    ADD_GATEWAY_TXN_NAME_KEY = 'destination_name'
    ADD_GATEWAY_TXN_PAYLOAD_KEY = 'destination_add_gateway_txn'
    ADD_GATEWAY_TXN_PAYLOAD_CONTENT_KEYS = [
        'address', 'fee', 'owner', 'payer', 'staking fee', 'txn'
    ]

    def __init__(self, diagnostics=[], **kwargs):
        """
        Intended to be used for constructing a DiagnosticsReport
        manually, or deserializing from JSON.

        When constructing manually, use this format:
            diagnostics = [
                ExampleDiagnostic()
            ]
            diagnostics_report = DiagnosticsReport(diagnostics)

        When deserializing from JSON string:
            report_json_str = '{"diagnostics_passed": false,
                                "errors": ["blah"], "ECC": false}'
            report = DiagnosticsReport.from_json_str(report_json_str)
        """
        super(DiagnosticsReport, self).__init__(kwargs)

        if DIAGNOSTICS_PASSED_KEY not in self:
            self.__setitem__(DIAGNOSTICS_PASSED_KEY, False)

        if DIAGNOSTICS_ERRORS_KEY not in self:
            self.__setitem__(DIAGNOSTICS_ERRORS_KEY, [])
        self.diagnostics = diagnostics

    def passed(self):
        return self[DIAGNOSTICS_PASSED_KEY]

    def set_passed(self, passed):
        self.__setitem__(DIAGNOSTICS_PASSED_KEY, passed)

    def append_error(self, key):
        self.__getitem__(DIAGNOSTICS_ERRORS_KEY).append(key)

    def get_errors(self):
        return self[DIAGNOSTICS_ERRORS_KEY]

    def get_missing_keys(self, required_keys: set) -> set:
        """
        Get required_keys that are missing from the DiagnosticsReport.

        Args:
            required_keys (set): Key names that should be present.

        Returns:
            set: Of keys that are missing
        """
        return required_keys.difference(self.keys())

    def has_manufacturing_errors(self) -> list:
        # Check only a subset of keys that are required for manufacturing
        # tests. If these don't have errors then we can conclude that device
        # is good from manufacturing point-of-view.
        errors = self.get_errors()

        if errors:
            manufacturing_errors = \
                self.KEYS_TO_CHECK_IN_MANUFACTUING.intersection(errors)

            return manufacturing_errors

        return []

    def validate_gateway_transaction_if_present(self) -> list:
        """
        Check if add gateway transaction data is present in this report and
        that it's valid.

        returns list:
            - If empty it means either there was no transaction data
            or it was valid.
            - In case of missing ADD_GATEWAY_TXN_PAYLOAD_KEY
            the ADD_GATEWAY_TXN_PAYLOAD_KEY is returned.
            - If payload is found but has missing or empty keys those
            keys are returned.
        """
        errors = []
        if self.ADD_GATEWAY_TXN_NAME_KEY in self.keys():
            if self.ADD_GATEWAY_TXN_PAYLOAD_KEY not in self.keys():
                return [self.ADD_GATEWAY_TXN_PAYLOAD_KEY]

            txn_payload = self.get(self.ADD_GATEWAY_TXN_PAYLOAD_KEY, {})
            if not txn_payload:
                return [self.ADD_GATEWAY_TXN_PAYLOAD_KEY + '.' + k
                        for k in self.ADD_GATEWAY_TXN_PAYLOAD_CONTENT_KEYS]

            for key in self.ADD_GATEWAY_TXN_PAYLOAD_CONTENT_KEYS:
                if key not in txn_payload or \
                        txn_payload[key] is None \
                        or txn_payload[key] == '':

                    errors.append(
                        self.ADD_GATEWAY_TXN_PAYLOAD_KEY + '.' + key)

        return errors

    def perform_diagnostics(self):
        self.__setitem__(DIAGNOSTICS_PASSED_KEY, True)
        for diagnostic in self.diagnostics:
            diagnostic.perform_test(self)

    def record_result(self, result, diagnostic):
        """
        Add the result to both key and friendly name, until key
        is deprecated.
        """
        self.__setitem__(diagnostic.key, result)
        # The current keys are terse. Let's migrate to human friendly ones.
        self.__setitem__(diagnostic.friendly_key, result)

    def record_failure(self, msg_or_exception, diagnostic):
        """
        Set the overall diagnostics status to failure and add this error
        to the list.
        """
        # If one test fails, then the overall state is a failure
        self.set_passed(False)

        # Add the failing key to list of errors
        self.append_error(diagnostic.key)
        self.append_error(diagnostic.friendly_key)

        # Provide additional details, like error message
        record_failure_as = msg_or_exception
        # Don't stringify bools
        if not isinstance(msg_or_exception, bool):
            record_failure_as = str(record_failure_as)
        self.record_result(record_failure_as, diagnostic)

    def get_report_subset(self, keys_to_extract):
        return {key: self.__getitem__(key) for key in keys_to_extract}

    def get_error_messages(self):
        def get_error_message(key):
            return "%s Error: %s" % (key, self.__getitem__(key))

        error_messages = map(get_error_message, self.get_errors())
        return ("\n").join(error_messages)

    @staticmethod
    def from_json_str(json_str):
        report_dict = json.loads(json_str)
        return DiagnosticsReport(report_dict)

    @staticmethod
    def from_json_dict(report_dict):
        return DiagnosticsReport(**report_dict)
