class BettingPreferences:
    def __init__(self, gambler_id, min_bet=1.0, max_bet=1000.0,
                 preferred_strategy="FIXED", auto_play=False, session_limit=100):
        self.gambler_id = gambler_id
        self.min_bet = float(min_bet)
        self.max_bet = float(max_bet)
        self.preferred_strategy = preferred_strategy
        self.auto_play = auto_play
        self.session_limit = session_limit
