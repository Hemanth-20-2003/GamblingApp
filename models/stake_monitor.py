class StakeMonitor:
    """In-memory real-time monitor; persisted via transactions."""
    def __init__(self, initial_stake):
        self.current_stake = float(initial_stake)
        self.peak_stake    = float(initial_stake)
        self.lowest_stake  = float(initial_stake)
        self.history       = [float(initial_stake)]

    def update(self, new_stake):
        self.current_stake = float(new_stake)
        self.history.append(self.current_stake)
        if self.current_stake > self.peak_stake:
            self.peak_stake = self.current_stake
        if self.current_stake < self.lowest_stake:
            self.lowest_stake = self.current_stake

    @property
    def volatility(self):
        if len(self.history) < 2:
            return 0.0
        avg = sum(self.history) / len(self.history)
        variance = sum((x - avg) ** 2 for x in self.history) / len(self.history)
        return variance ** 0.5  # std-dev as volatility proxy
