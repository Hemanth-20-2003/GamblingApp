"""Limit validation exception for UC6 Input Validation"""
from exceptions.validation_exception import ValidationException


class LimitValidationException(ValidationException):
    def __init__(self, field, attempted_value=None, message=""):
        super().__init__("LIMIT_ERROR", field, attempted_value,
                         message or f"Limit validation error on '{field}'")
