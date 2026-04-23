"""Base validation exception for UC6 Input Validation"""


class ValidationException(Exception):
    def __init__(self, error_type: str, field: str,
                 attempted_value=None, message: str = ""):
        self.error_type     = error_type
        self.field          = field
        self.attempted_value = attempted_value
        self.message        = message or f"Validation failed for '{field}'"
        super().__init__(self.message)
