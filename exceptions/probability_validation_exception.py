"""Probability validation exception for UC6 Input Validation"""
from exceptions.validation_exception import ValidationException


class ProbabilityValidationException(ValidationException):
    def __init__(self, field, attempted_value=None, message=""):
        super().__init__("PROBABILITY_ERROR", field, attempted_value,
                         message or f"Probability validation error on '{field}'")
