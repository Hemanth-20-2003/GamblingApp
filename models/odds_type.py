"""Odds type enum for UC5 Win/Loss Calculation"""
from enum import Enum


class OddsType(Enum):
    FIXED             = "FIXED"
    PROBABILITY_BASED = "PROBABILITY_BASED"
    AMERICAN          = "AMERICAN"
    DECIMAL           = "DECIMAL"
