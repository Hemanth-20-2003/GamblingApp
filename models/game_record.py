"""Game record data class for UC4 Game Session Management"""
from datetime import datetime


class GameRecord:
    def __init__(self, session_id, gambler_id, game_number,
                 bet_amount, outcome, payout, stake_before, stake_after):
        self.session_id   = session_id
        self.gambler_id   = gambler_id
        self.game_number  = game_number
        self.bet_amount   = float(bet_amount)
        self.outcome      = outcome   # "WIN" or "LOSS"
        self.payout       = float(payout)
        self.stake_before = float(stake_before)
        self.stake_after  = float(stake_after)
        self.duration_sec = 0.0
        self.played_at    = datetime.now()
        self.id           = None
from datetime import datetime


class GameRecord:
    def __init__(self, session_id, gambler_id, game_number,
                 bet_amount, outcome, payout, stake_before, stake_after):
        self.session_id   = session_id
        self.gambler_id   = gambler_id
        self.game_number  = game_number
        self.bet_amount   = float(bet_amount)
        self.outcome      = outcome   # "WIN" or "LOSS"
        self.payout       = float(payout)
        self.stake_before = float(stake_before)
        self.stake_after  = float(stake_after)
        self.duration_sec = 0.0
        self.played_at    = datetime.now()
        self.id           = None
