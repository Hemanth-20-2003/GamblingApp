from abc import ABC, abstractmethod


class BettingStrategy(ABC):
    @abstractmethod
    def calculate_bet(self, current_stake: float, last_bet: float,
                      last_won: bool, base_bet: float) -> float:
        pass

    @property
    def name(self):
        return self.__class__.__name__


class FixedAmountStrategy(BettingStrategy):
    def __init__(self, fixed_amount):
        self.fixed_amount = float(fixed_amount)

    def calculate_bet(self, current_stake, last_bet, last_won, base_bet):
        return min(self.fixed_amount, current_stake)


class PercentageStrategy(BettingStrategy):
    def __init__(self, percent=5.0):
        self.percent = percent  # e.g. 5 means 5%

    def calculate_bet(self, current_stake, last_bet, last_won, base_bet):
        return round(current_stake * self.percent / 100, 2)


class MartingaleStrategy(BettingStrategy):
    """Double after loss, reset to base after win."""
    def calculate_bet(self, current_stake, last_bet, last_won, base_bet):
        if last_bet == 0 or last_won:
            return base_bet
        return min(last_bet * 2, current_stake)


class ReverseMartingaleStrategy(BettingStrategy):
    """Double after win, reset to base after loss."""
    def calculate_bet(self, current_stake, last_bet, last_won, base_bet):
        if last_bet == 0 or not last_won:
            return base_bet
        return min(last_bet * 2, current_stake)


class FibonacciStrategy(BettingStrategy):
    """Progress through Fibonacci on losses, step back on win."""
    FIB = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]

    def __init__(self):
        self._idx = 0

    def calculate_bet(self, current_stake, last_bet, last_won, base_bet):
        if last_won:
            self._idx = max(0, self._idx - 2)
        else:
            self._idx = min(self._idx + 1, len(self.FIB) - 1)
        return min(self.FIB[self._idx] * base_bet, current_stake)


class DAlembertStrategy(BettingStrategy):
    """Increase by 1 unit after loss, decrease by 1 unit after win."""
    def calculate_bet(self, current_stake, last_bet, last_won, base_bet):
        if last_bet == 0:
            return base_bet
        if last_won:
            return max(base_bet, last_bet - base_bet)
        return min(last_bet + base_bet, current_stake)


STRATEGIES = {
    "FIXED":            FixedAmountStrategy,
    "PERCENTAGE":       PercentageStrategy,
    "MARTINGALE":       MartingaleStrategy,
    "REVERSE_MARTINGALE": ReverseMartingaleStrategy,
    "FIBONACCI":        FibonacciStrategy,
    "DALEMBERT":        DAlembertStrategy,
}
