class Diagnostic():
    """
    Pseudo-interface class that should be extended in order to add
    a type of diagnostic reading to a DiagnosticReport.
    """

    def __init__(self, key, friendly_key):
        """
        key - Key of relevant value in diagnostics_report dictionary
        friendly_key - Same as key but a human_friendly_snake_case
                        version. To replace key eventually.
        """
        self.key = key
        self.friendly_key = friendly_key

    def perform_test(self, diagnostics_report):
        raise Exception("Should be implemented by extending class")
