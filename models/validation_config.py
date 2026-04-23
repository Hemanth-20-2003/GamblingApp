"""Validation configuration for UC6 Input Validation"""


class ValidationConfig:
    def __init__(self):
        self.min_stake       = 10.0
        self.max_stake       = 1_000_000.0
        self.min_bet         = 0.01
        self.max_bet         = 100_000.0
        self.min_probability = 0.01
        self.max_probability = 0.99
        self.strict_mode     = False
        self.allow_zero_stake = False
