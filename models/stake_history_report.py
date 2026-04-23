class StakeHistoryReport:
    def __init__(self, transactions: list, monitor):
        self.transactions = transactions
        self.monitor      = monitor

    def summary(self):
        wins   = [t for t in self.transactions if t["transaction_type"] == "BET_WIN"]
        losses = [t for t in self.transactions if t["transaction_type"] == "BET_LOSS"]
        total_won  = sum(float(t["amount"]) for t in wins)
        total_lost = sum(float(t["amount"]) for t in losses)
        return {
            "total_transactions": len(self.transactions),
            "total_won":          round(total_won, 2),
            "total_lost":         round(total_lost, 2),
            "net_profit_loss":    round(total_won - total_lost, 2),
            "peak_stake":         round(self.monitor.peak_stake, 2),
            "lowest_stake":       round(self.monitor.lowest_stake, 2),
            "volatility":         round(self.monitor.volatility, 4),
        }

    def print_report(self):
        s = self.summary()
        print("\n===== STAKE HISTORY REPORT =====")
        for k, v in s.items():
            print(f"  {k:<22}: {v}")
        print("\n  Transactions:")
        for t in self.transactions[-10:]:  # last 10
            print(f"    [{t['created_at']}] {t['transaction_type']:15} "
                  f"amount={float(t['amount']):>10.2f}  "
                  f"balance={float(t['balance_after']):>10.2f}")
        print("================================\n")
