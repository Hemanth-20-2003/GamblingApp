"""Validation result for UC6 Input Validation"""


class ValidationResult:
    def __init__(self):
        self.errors: list  = []
        self.warnings: list = []

    @property
    def is_valid(self):
        return len(self.errors) == 0

    def add_error(self, msg):
        self.errors.append(msg)

    def add_warning(self, msg):
        self.warnings.append(msg)

    def report(self):
        lines = ["=== VALIDATION RESULT ===",
                 f"Valid: {self.is_valid}"]
        if self.errors:
            lines.append("Errors:")
            lines += [f"  ✗ {e}" for e in self.errors]
        if self.warnings:
            lines.append("Warnings:")
            lines += [f"  ⚠ {w}" for w in self.warnings]
        return "\n".join(lines)
