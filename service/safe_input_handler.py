"""Safe input handler utility for UC6 Input Validation"""
from service.input_validator import InputValidator


class SafeInputHandler:
    def __init__(self, validator: InputValidator):
        self.validator = validator

    def prompt_stake(self, prompt="Enter initial stake: ") -> float:
        while True:
            raw = input(prompt)
            val, r = self.validator.parse_and_validate_numeric(raw, "stake")
            if val is not None:
                r2 = self.validator.validate_initial_stake(val)
                if r2.is_valid:
                    return val
                print(r2.report())
            else:
                print(r.report())

    def prompt_bet(self, current_stake: float,
                   prompt="Enter bet amount: ") -> float:
        while True:
            raw = input(prompt)
            val, r = self.validator.parse_and_validate_numeric(raw, "bet")
            if val is not None:
                r2 = self.validator.validate_bet_amount(val, current_stake)
                if r2.is_valid:
                    return val
                print(r2.report())
            else:
                print(r.report())

    def prompt_probability(self, prompt="Enter win probability (0-1): ") -> float:
        while True:
            raw = input(prompt)
            val, r = self.validator.parse_and_validate_numeric(raw, "probability")
            if val is not None:
                r2 = self.validator.validate_probability(val)
                if r2.is_valid:
                    return val
                print(r2.report())
            else:
                print(r.report())
