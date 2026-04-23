"""Odds configuration for UC5 Win/Loss Calculation"""
from models.odds_type import OddsType


class OddsConfig:
    def __init__(self, odds_type: OddsType, value: float):
        self.odds_type = odds_type
        self.value     = float(value)

    def calculate_payout(self, bet_amount: float, win_probability: float = 0.5) -> float:
        """Return NET profit (not total payout) on a win."""
        if self.odds_type == OddsType.FIXED:
            return round(bet_amount * (self.value - 1), 4)
        elif self.odds_type == OddsType.PROBABILITY_BASED:
            fair_odds = 1.0 / win_probability if win_probability > 0 else 2.0
            return round(bet_amount * (fair_odds - 1), 4)
        elif self.odds_type == OddsType.AMERICAN:
            if self.value > 0:     # underdog: e.g. +150 means win 150 per 100
                return round(bet_amount * self.value / 100, 4)
            else:                  # favorite: e.g. -150 means bet 150 to win 100
                return round(bet_amount * 100 / abs(self.value), 4)
        elif self.odds_type == OddsType.DECIMAL:
            return round(bet_amount * (self.value - 1), 4)
        return bet_amount
