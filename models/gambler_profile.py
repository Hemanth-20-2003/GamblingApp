from datetime import datetime


class GamblerProfile:
    def __init__(self, name, email, initial_stake, win_threshold, loss_threshold):
        self.name = name
        self.email = email
        self.initial_stake = float(initial_stake)
        self.current_stake = float(initial_stake)
        self.win_threshold = float(win_threshold)
        self.loss_threshold = float(loss_threshold)
        self.is_active = True
        self.created_at = datetime.now()
        self.id = None  # set after DB insert

    def __repr__(self):
        return (f"GamblerProfile(id={self.id}, name={self.name}, "
                f"stake={self.current_stake:.2f}, win_thresh={self.win_threshold:.2f}, "
                f"loss_thresh={self.loss_threshold:.2f})")
