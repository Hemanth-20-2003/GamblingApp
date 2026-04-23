"""Stake validation exception for UC6 Input Validation"""
from exceptions.validation_exception import ValidationException


class StakeValidationException(ValidationException):
    def __init__(self, field, attempted_value=None, message=""):
        super().__init__("STAKE_ERROR", field, attempted_value,
                         message or f"Stake validation error on '{field}'")
