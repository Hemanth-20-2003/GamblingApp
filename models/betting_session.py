class BettingSession:
    def __init__(self, gambler_id, session_id):
        self.gambler_id = gambler_id
        self.session_id = session_id
        self.bets: list = []

    def add_bet(self, bet):
        self.bets.append(bet)

    def summary(self):
        wins   = [b for b in self.bets if b.outcome == "WIN"]
        losses = [b for b in self.bets if b.outcome == "LOSS"]
        return {
            "total_bets":   len(self.bets),
            "wins":         len(wins),
            "losses":       len(losses),
            "total_wagered": round(sum(b.bet_amount for b in self.bets), 2),
            "total_won":    round(sum(b.actual_payout for b in wins), 2),
            "total_lost":   round(sum(b.bet_amount for b in losses), 2),
        }
