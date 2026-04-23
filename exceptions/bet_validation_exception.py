"""Bet validation exception for UC6 Input Validation"""
from exceptions.validation_exception import ValidationException


class BetValidationException(ValidationException):
    def __init__(self, field, attempted_value=None, message=""):
        super().__init__("BET_ERROR", field, attempted_value,
                         message or f"Bet validation error on '{field}'")
