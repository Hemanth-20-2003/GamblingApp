"""Input validator service for UC6 Input Validation"""
from datetime import datetime
from config.db import get_connection, insert
from models.validation_result import ValidationResult
from models.validation_config import ValidationConfig


class InputValidator:
    def __init__(self, config: ValidationConfig = None, gambler_id: int = None):
        self.config     = config or ValidationConfig()
        self.gambler_id = gambler_id

    def _log_error(self, field, attempted_value, error_type, message,
                   is_warning=False):
        """Persist validation event to DB (fire-and-forget)."""
        try:
            conn = get_connection()
            try:
                insert(conn,
                    """INSERT INTO validation_logs
                       (gambler_id, field_name, attempted_value,
                        error_type, error_message, is_warning, logged_at)
                       VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                    (self.gambler_id, field, str(attempted_value),
                     error_type, message, is_warning, datetime.now()))
                conn.commit()
            finally:
                conn.close()
        except Exception:
            pass  # Logging failure must never break the main flow

    # ── 1. Validate initial stake ─────────────
    def validate_initial_stake(self, stake) -> ValidationResult:
        r = ValidationResult()
        try:
            val = float(stake)
        except (TypeError, ValueError):
            msg = f"Stake '{stake}' is not a valid number"
            r.add_error(msg)
            self._log_error("initial_stake", stake, "NUMERIC_ERROR", msg)
            return r

        import math
        if math.isnan(val) or math.isinf(val):
            msg = f"Stake '{stake}' is NaN or Infinity"
            r.add_error(msg)
            self._log_error("initial_stake", stake, "NUMERIC_ERROR", msg)
            return r

        if val < 0:
            msg = f"Stake {val} is negative"
            r.add_error(msg)
            self._log_error("initial_stake", val, "STAKE_ERROR", msg)
        elif val == 0 and not self.config.allow_zero_stake:
            msg = "Stake cannot be zero"
            r.add_error(msg)
            self._log_error("initial_stake", val, "STAKE_ERROR", msg)
        elif val < self.config.min_stake:
            msg = f"Stake {val} is below minimum {self.config.min_stake}"
            r.add_error(msg)
            self._log_error("initial_stake", val, "RANGE_ERROR", msg)
        elif val > self.config.max_stake:
            msg = f"Stake {val} exceeds maximum {self.config.max_stake}"
            r.add_error(msg)
            self._log_error("initial_stake", val, "RANGE_ERROR", msg)
        elif val < self.config.min_stake * 2:
            r.add_warning(f"Stake {val} is low (close to minimum)")

        return r

    # ── 2. Validate bet amount ────────────────
    def validate_bet_amount(self, bet_amount, current_stake) -> ValidationResult:
        r = ValidationResult()
        try:
            bet   = float(bet_amount)
            stake = float(current_stake)
        except (TypeError, ValueError) as e:
            r.add_error(f"Invalid numeric input: {e}")
            return r

        if bet <= 0:
            msg = f"Bet {bet} must be positive"
            r.add_error(msg)
            self._log_error("bet_amount", bet, "BET_ERROR", msg)

        if bet > stake:
            msg = f"Bet {bet} exceeds current stake {stake}"
            r.add_error(msg)
            self._log_error("bet_amount", bet, "BET_ERROR", msg)

        if bet < self.config.min_bet:
            msg = f"Bet {bet} below minimum {self.config.min_bet}"
            r.add_error(msg)
            self._log_error("bet_amount", bet, "RANGE_ERROR", msg)

        if bet > self.config.max_bet:
            msg = f"Bet {bet} exceeds maximum {self.config.max_bet}"
            r.add_error(msg)
            self._log_error("bet_amount", bet, "RANGE_ERROR", msg)

        if bet > stake * 0.5:
            r.add_warning(f"Bet {bet} is more than 50% of stake {stake}")

        return r

    # ── 3. Validate limits ────────────────────
    def validate_limits(self, upper_limit, lower_limit,
                        initial_stake=None) -> ValidationResult:
        r = ValidationResult()
        try:
            upper = float(upper_limit)
            lower = float(lower_limit)
        except (TypeError, ValueError) as e:
            r.add_error(f"Invalid limit value: {e}")
            return r

        if lower < 0:
            msg = f"Lower limit {lower} cannot be negative"
            r.add_error(msg)
            self._log_error("lower_limit", lower, "LIMIT_ERROR", msg)

        if upper <= lower:
            msg = f"Upper limit {upper} must be > lower limit {lower}"
            r.add_error(msg)
            self._log_error("upper_limit", upper, "LIMIT_ERROR", msg)

        if initial_stake is not None:
            try:
                stake = float(initial_stake)
                if stake <= lower:
                    msg = f"Stake {stake} must be above lower limit {lower}"
                    r.add_error(msg)
                if stake >= upper:
                    msg = f"Stake {stake} must be below upper limit {upper}"
                    r.add_error(msg)
            except (TypeError, ValueError):
                r.add_error("Invalid initial_stake value")

        return r

    # ── 4. Parse and validate numeric input ───
    def parse_and_validate_numeric(self, raw_input: str,
                                   field_name: str = "value") -> tuple:
        """
        Returns (float_value, ValidationResult).
        float_value is None on parse failure.
        """
        import math
        r = ValidationResult()

        if raw_input is None or str(raw_input).strip() == "":
            r.add_error(f"'{field_name}' is empty or null")
            self._log_error(field_name, raw_input, "NULL_ERROR",
                            f"Empty or null input for {field_name}")
            return None, r

        try:
            val = float(str(raw_input).strip())
        except ValueError:
            msg = f"'{raw_input}' is not a valid number for '{field_name}'"
            r.add_error(msg)
            self._log_error(field_name, raw_input, "NUMERIC_ERROR", msg)
            return None, r

        if math.isnan(val):
            msg = f"'{field_name}' resolved to NaN"
            r.add_error(msg)
            self._log_error(field_name, raw_input, "NUMERIC_ERROR", msg)
            return None, r

        if math.isinf(val):
            msg = f"'{field_name}' resolved to Infinity"
            r.add_error(msg)
            self._log_error(field_name, raw_input, "NUMERIC_ERROR", msg)
            return None, r

        return val, r

    # ── 5. Prevent negative stakes ────────────
    def validate_stake_non_negative(self, stake) -> ValidationResult:
        r = ValidationResult()
        try:
            val = float(stake)
        except (TypeError, ValueError):
            r.add_error(f"Invalid stake value '{stake}'")
            return r

        if val < 0:
            msg = f"Stake {val} is negative — not allowed"
            r.add_error(msg)
            self._log_error("stake", val, "STAKE_ERROR", msg)
        elif val == 0 and not self.config.allow_zero_stake:
            if self.config.strict_mode:
                r.add_error("Stake is zero (strict mode)")
                self._log_error("stake", val, "STAKE_ERROR", "Zero stake in strict mode")
            else:
                r.add_warning("Stake is zero")

        return r

    # ── 6. Validate probability ───────────────
    def validate_probability(self, probability) -> ValidationResult:
        r = ValidationResult()
        import math

        try:
            prob = float(probability)
        except (TypeError, ValueError):
            msg = f"'{probability}' is not a valid probability"
            r.add_error(msg)
            self._log_error("probability", probability, "PROBABILITY_ERROR", msg)
            return r

        if math.isnan(prob) or math.isinf(prob):
            msg = f"Probability '{probability}' is NaN or Infinity"
            r.add_error(msg)
            self._log_error("probability", probability, "PROBABILITY_ERROR", msg)
            return r

        if prob < 0 or prob > 1:
            msg = f"Probability {prob} must be between 0 and 1"
            r.add_error(msg)
            self._log_error("probability", prob, "PROBABILITY_ERROR", msg)
        elif prob < self.config.min_probability:
            msg = f"Probability {prob} is below configured minimum {self.config.min_probability}"
            r.add_error(msg)
        elif prob > self.config.max_probability:
            msg = f"Probability {prob} exceeds configured maximum {self.config.max_probability}"
            r.add_error(msg)
        elif prob < 0.1 or prob > 0.9:
            r.add_warning(f"Probability {prob} is extreme — outcomes will be highly skewed")

        return r

    # ── Comprehensive validation ──────────────
    def validate_all(self, initial_stake, bet_amount=None,
                     upper_limit=None, lower_limit=None,
                     probability=None) -> ValidationResult:
        combined = ValidationResult()

        for r in [self.validate_initial_stake(initial_stake)]:
            combined.errors   += r.errors
            combined.warnings += r.warnings

        if bet_amount is not None:
            r = self.validate_bet_amount(bet_amount, initial_stake)
            combined.errors   += r.errors
            combined.warnings += r.warnings

        if upper_limit is not None and lower_limit is not None:
            r = self.validate_limits(upper_limit, lower_limit, initial_stake)
            combined.errors   += r.errors
            combined.warnings += r.warnings

        if probability is not None:
            r = self.validate_probability(probability)
            combined.errors   += r.errors
            combined.warnings += r.warnings

        return combined
