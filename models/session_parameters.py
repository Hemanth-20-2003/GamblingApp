"""Session parameters validation for UC4 Game Session Management"""


class SessionParameters:
    def __init__(self, upper_limit, lower_limit, min_bet=1.0,
                 max_bet=500.0, max_games=500,
                 max_duration_seconds=3600, win_probability=0.5):
        if upper_limit <= lower_limit:
            raise ValueError("Upper limit must be greater than lower limit")
        self.upper_limit          = float(upper_limit)
        self.lower_limit          = float(lower_limit)
        self.min_bet              = float(min_bet)
        self.max_bet              = float(max_bet)
        self.max_games            = int(max_games)
        self.max_duration_seconds = int(max_duration_seconds)
        self.win_probability      = float(win_probability)
class SessionParameters:
    def __init__(self, upper_limit, lower_limit, min_bet=1.0,
                 max_bet=500.0, max_games=500,
                 max_duration_seconds=3600, win_probability=0.5):
        if upper_limit <= lower_limit:
            raise ValueError("Upper limit must be greater than lower limit")
        self.upper_limit          = float(upper_limit)
        self.lower_limit          = float(lower_limit)
        self.min_bet              = float(min_bet)
        self.max_bet              = float(max_bet)
        self.max_games            = int(max_games)
        self.max_duration_seconds = int(max_duration_seconds)
        self.win_probability      = float(win_probability)
