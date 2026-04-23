from datetime import datetime


class Bet:
    def __init__(self, gambler_id, session_id, strategy_name,
                 bet_amount, win_probability, odds, stake_before):
        self.gambler_id      = gambler_id
        self.session_id      = session_id
        self.strategy        = strategy_name
        self.bet_amount      = float(bet_amount)
        self.win_probability = float(win_probability)
        self.odds            = float(odds)
        self.potential_win   = round(bet_amount * (odds - 1), 2)
        self.outcome         = "PENDING"
        self.actual_payout   = 0.0
        self.stake_before    = float(stake_before)
        self.stake_after     = None
        self.placed_at       = datetime.now()
        self.settled_at      = None
        self.id              = None

    def settle(self, won: bool):
        self.outcome = "WIN" if won else "LOSS"
        self.actual_payout = self.potential_win if won else 0.0
        self.stake_after = (self.stake_before + self.potential_win
                            if won else self.stake_before - self.bet_amount)
        self.settled_at = datetime.now()

    def __repr__(self):
        return (f"Bet(id={self.id}, amount={self.bet_amount:.2f}, "
                f"strategy={self.strategy}, outcome={self.outcome}, "
                f"payout={self.actual_payout:.2f})")
