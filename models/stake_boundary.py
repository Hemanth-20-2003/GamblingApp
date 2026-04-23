class StakeBoundary:
    def __init__(self, gambler_id, upper_limit, lower_limit):
        self.gambler_id  = gambler_id
        self.upper_limit = float(upper_limit)
        self.lower_limit = float(lower_limit)
        # Warning zones: 20% above min, 80% of max
        self.warning_lower = lower_limit + (upper_limit - lower_limit) * 0.20
        self.warning_upper = lower_limit + (upper_limit - lower_limit) * 0.80

    def is_within_bounds(self, stake):
        return self.lower_limit <= stake <= self.upper_limit

    def check_warnings(self, stake):
        warnings = []
        if stake <= self.warning_lower:
            warnings.append(f"WARNING: Stake {stake:.2f} approaching lower limit {self.lower_limit:.2f}")
        if stake >= self.warning_upper:
            warnings.append(f"WARNING: Stake {stake:.2f} approaching upper limit {self.upper_limit:.2f}")
        return warnings
