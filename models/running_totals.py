"""Running totals tracking for UC5 Win/Loss Calculation"""
from models.game_result import GameResult


class RunningTotals:
    def __init__(self, initial_balance):
        self.initial_balance      = float(initial_balance)
        self.cumulative_winnings  = 0.0
        self.cumulative_losses    = 0.0
        self.balance_history      = [float(initial_balance)]

    @property
    def net_profit_loss(self):
        return round(self.cumulative_winnings - self.cumulative_losses, 2)

    @property
    def current_balance(self):
        return self.balance_history[-1] if self.balance_history else self.initial_balance

    def update(self, result: GameResult):
        if result.outcome == "WIN":
            self.cumulative_winnings += result.net_change
        else:
            self.cumulative_losses += abs(result.net_change)
        self.balance_history.append(result.stake_after)
