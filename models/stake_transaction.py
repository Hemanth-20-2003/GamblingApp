from datetime import datetime


class StakeTransaction:
    def __init__(self, gambler_id, session_id, tx_type,
                 amount, balance_before, balance_after, bet_id=None, note=""):
        self.gambler_id     = gambler_id
        self.session_id     = session_id
        self.transaction_type = tx_type.value
        self.amount         = float(amount)
        self.balance_before = float(balance_before)
        self.balance_after  = float(balance_after)
        self.bet_id         = bet_id
        self.note           = note
        self.created_at     = datetime.now()
        self.id             = None
