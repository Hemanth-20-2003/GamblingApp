"""Win/Loss statistics tracking for UC5 Win/Loss Calculation"""
from models.game_result import GameResult


class WinLossStatistics:
    def __init__(self):
        self.total_wins     = 0
        self.total_losses   = 0
        self.total_pushes   = 0
        self.total_winnings = 0.0
        self.total_losses_amount = 0.0
        self.largest_win    = 0.0
        self.largest_loss   = 0.0
        self.current_win_streak  = 0
        self.current_loss_streak = 0
        self.longest_win_streak  = 0
        self.longest_loss_streak = 0

    @property
    def total_games(self):
        return self.total_wins + self.total_losses + self.total_pushes

    @property
    def win_rate(self):
        return (self.total_wins / self.total_games * 100) if self.total_games else 0.0

    @property
    def win_loss_ratio(self):
        return (self.total_wins / self.total_losses) if self.total_losses else float('inf')

    @property
    def net_profit_loss(self):
        return round(self.total_winnings - self.total_losses_amount, 2)

    @property
    def profit_factor(self):
        return (self.total_winnings / self.total_losses_amount
                if self.total_losses_amount else float('inf'))

    def record(self, result: GameResult):
        if result.outcome == "WIN":
            self.total_wins += 1
            self.total_winnings += result.net_change
            self.largest_win = max(self.largest_win, result.net_change)
            self.current_win_streak  += 1
            self.current_loss_streak  = 0
            self.longest_win_streak  = max(self.longest_win_streak,
                                           self.current_win_streak)
        elif result.outcome == "LOSS":
            self.total_losses += 1
            self.total_losses_amount += abs(result.net_change)
            self.largest_loss = max(self.largest_loss, abs(result.net_change))
            self.current_loss_streak += 1
            self.current_win_streak   = 0
            self.longest_loss_streak = max(self.longest_loss_streak,
                                           self.current_loss_streak)
        else:
            self.total_pushes += 1

    def to_dict(self):
        return {
            "total_games":         self.total_games,
            "wins":                self.total_wins,
            "losses":              self.total_losses,
            "win_rate_%":          round(self.win_rate, 2),
            "win_loss_ratio":      round(self.win_loss_ratio, 4),
            "net_profit_loss":     self.net_profit_loss,
            "profit_factor":       round(self.profit_factor, 4),
            "largest_win":         round(self.largest_win, 2),
            "largest_loss":        round(self.largest_loss, 2),
            "current_win_streak":  self.current_win_streak,
            "current_loss_streak": self.current_loss_streak,
            "longest_win_streak":  self.longest_win_streak,
            "longest_loss_streak": self.longest_loss_streak,
        }
