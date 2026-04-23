"""Game result data class for UC5 Win/Loss Calculation"""
from datetime import datetime
from models.odds_config import OddsConfig


class GameResult:
    def __init__(self, session_id, gambler_id, game_number,
                 bet_amount, win_probability, odds_config: OddsConfig,
                 stake_before):
        self.session_id      = session_id
        self.gambler_id      = gambler_id
        self.game_number     = game_number
        self.bet_amount      = float(bet_amount)
        self.win_probability = float(win_probability)
        self.odds_config     = odds_config
        self.stake_before    = float(stake_before)
        self.outcome         = None   # "WIN" / "LOSS"
        self.net_change      = 0.0
        self.stake_after     = float(stake_before)
        self.played_at       = datetime.now()

    def resolve(self, won: bool):
        self.outcome = "WIN" if won else "LOSS"
        if won:
            profit = self.odds_config.calculate_payout(
                self.bet_amount, self.win_probability)
            self.net_change = profit
        else:
            self.net_change = -self.bet_amount
        self.stake_after = round(self.stake_before + self.net_change, 4)
