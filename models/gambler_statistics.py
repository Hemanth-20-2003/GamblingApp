class GamblerStatisticsDTO:
    def __init__(self, row):
        """Build from a DB row dict."""
        self.gambler_id   = row.get("gambler_id")
        self.total_bets   = row.get("total_bets", 0)
        self.total_wins   = row.get("total_wins", 0)
        self.total_losses = row.get("total_losses", 0)
        self.total_winnings  = float(row.get("total_winnings", 0))
        self.total_lost      = float(row.get("total_lost", 0))
        self.largest_win  = float(row.get("largest_win", 0))
        self.largest_loss = float(row.get("largest_loss", 0))

    @property
    def win_rate(self):
        return (self.total_wins / self.total_bets * 100) if self.total_bets else 0.0

    @property
    def net_profit_loss(self):
        return self.total_winnings - self.total_lost

    def __repr__(self):
        return (f"Stats(bets={self.total_bets}, wins={self.total_wins}, "
                f"win_rate={self.win_rate:.1f}%, net={self.net_profit_loss:.2f})")
