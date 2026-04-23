from config.db import get_connection, execute_query, execute_one, insert
from models import (
    TransactionType, StakeTransaction, StakeBoundary,
    StakeMonitor, StakeHistoryReport
)


class StakeManagementService:
    # Keep per-gambler monitors in memory for the current run
    _monitors: dict = {}

    def _get_current_stake(self, conn, gambler_id):
        row = execute_one(conn, "SELECT current_stake FROM gamblers WHERE id=%s",
                          (gambler_id,))
        if not row:
            raise ValueError(f"Gambler id={gambler_id} not found")
        return float(row["current_stake"])

    def _record_transaction(self, conn, gambler_id, session_id,
                            tx_type: TransactionType, amount,
                            balance_before, balance_after,
                            bet_id=None, note=""):
        tx = StakeTransaction(gambler_id, session_id, tx_type,
                              amount, balance_before, balance_after, bet_id, note)
        tx.id = insert(conn,
            """INSERT INTO stake_transactions
               (gambler_id, session_id, transaction_type, amount,
                balance_before, balance_after, bet_id, note, created_at)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (gambler_id, session_id, tx.transaction_type, amount,
             balance_before, balance_after, bet_id, note, tx.created_at))
        return tx

    # ── 1. Initialize ────────────────────────
    def initialize_stake(self, gambler_id: int, initial_stake: float,
                         upper_limit: float, lower_limit: float,
                         session_id: int = None) -> StakeMonitor:
        """Validate and set up initial stake + boundary in DB."""
        boundary = StakeBoundary(gambler_id, upper_limit, lower_limit)
        if not boundary.is_within_bounds(initial_stake):
            raise ValueError(
                f"Initial stake {initial_stake} not within bounds "
                f"[{lower_limit}, {upper_limit}]")

        conn = get_connection()
        try:
            # Save boundary
            insert(conn,
                """INSERT INTO stake_boundaries
                   (gambler_id, upper_limit, lower_limit, warning_lower, warning_upper)
                   VALUES (%s,%s,%s,%s,%s)""",
                (gambler_id, upper_limit, lower_limit,
                 boundary.warning_lower, boundary.warning_upper))

            # Record INITIAL_STAKE transaction
            self._record_transaction(conn, gambler_id, session_id,
                                     TransactionType.INITIAL_STAKE,
                                     initial_stake, 0.0, initial_stake,
                                     note="Session initialized")

            # Update gambler current_stake
            execute_query(conn,
                "UPDATE gamblers SET current_stake=%s WHERE id=%s",
                (initial_stake, gambler_id))

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

        monitor = StakeMonitor(initial_stake)
        self._monitors[gambler_id] = monitor
        print(f"[INIT STAKE] Gambler {gambler_id}: stake={initial_stake:.2f} "
              f"bounds=[{lower_limit:.2f}, {upper_limit:.2f}]")
        return monitor

    # ── 2. Track ─────────────────────────────
    def track_stake(self, gambler_id: int) -> StakeMonitor:
        """Return (or create) the in-memory StakeMonitor for a gambler."""
        if gambler_id not in self._monitors:
            conn = get_connection()
            try:
                stake = self._get_current_stake(conn, gambler_id)
            finally:
                conn.close()
            self._monitors[gambler_id] = StakeMonitor(stake)
        return self._monitors[gambler_id]

    # ── 3. Calculate after bet ────────────────
    def calculate_after_bet(self, gambler_id: int, bet_amount: float,
                            won: bool, payout: float = None,
                            session_id: int = None, bet_id: int = None) -> float:
        """Process a bet result and update DB + monitor."""
        conn = get_connection()
        try:
            balance_before = self._get_current_stake(conn, gambler_id)

            if won:
                actual_payout = payout if payout is not None else bet_amount
                balance_after = balance_before + actual_payout
                tx_type = TransactionType.BET_WIN
                note = f"Won {actual_payout:.2f}"
            else:
                balance_after = balance_before - bet_amount
                tx_type = TransactionType.BET_LOSS
                actual_payout = bet_amount
                note = f"Lost {bet_amount:.2f}"

            execute_query(conn,
                "UPDATE gamblers SET current_stake=%s WHERE id=%s",
                (balance_after, gambler_id))

            self._record_transaction(conn, gambler_id, session_id, tx_type,
                                     actual_payout, balance_before, balance_after,
                                     bet_id, note)
            conn.commit()

            # Update in-memory monitor
            monitor = self._monitors.get(gambler_id)
            if monitor:
                monitor.update(balance_after)

            print(f"[STAKE CALC] {'WIN' if won else 'LOSS'}: "
                  f"{balance_before:.2f} → {balance_after:.2f}")
            return balance_after
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ── 4. Monitor fluctuations ───────────────
    def monitor_fluctuations(self, gambler_id: int) -> dict:
        monitor = self.track_stake(gambler_id)
        return {
            "current_stake": round(monitor.current_stake, 2),
            "peak_stake":    round(monitor.peak_stake, 2),
            "lowest_stake":  round(monitor.lowest_stake, 2),
            "volatility":    round(monitor.volatility, 4),
            "total_changes": len(monitor.history) - 1,
        }

    # ── 5. Validate boundaries ────────────────
    def validate_boundaries(self, gambler_id: int) -> dict:
        conn = get_connection()
        try:
            stake = self._get_current_stake(conn, gambler_id)
            b_row = execute_one(conn,
                "SELECT * FROM stake_boundaries WHERE gambler_id=%s ORDER BY id DESC LIMIT 1",
                (gambler_id,))
            if not b_row:
                return {"valid": True, "warnings": [], "stake": stake}

            boundary = StakeBoundary(gambler_id,
                                     float(b_row["upper_limit"]),
                                     float(b_row["lower_limit"]))
            return {
                "valid":    boundary.is_within_bounds(stake),
                "warnings": boundary.check_warnings(stake),
                "stake":    stake,
                "upper":    boundary.upper_limit,
                "lower":    boundary.lower_limit,
            }
        finally:
            conn.close()

    # ── 6. Generate history report ────────────
    def generate_report(self, gambler_id: int,
                        session_id: int = None,
                        tx_type_filter: str = None) -> StakeHistoryReport:
        conn = get_connection()
        try:
            query = "SELECT * FROM stake_transactions WHERE gambler_id=%s"
            params = [gambler_id]
            if session_id:
                query += " AND session_id=%s"
                params.append(session_id)
            if tx_type_filter:
                query += " AND transaction_type=%s"
                params.append(tx_type_filter)
            query += " ORDER BY created_at ASC"
            rows = execute_query(conn, query, params, fetch=True)
        finally:
            conn.close()

        monitor = self._monitors.get(gambler_id, StakeMonitor(0))
        return StakeHistoryReport(rows, monitor)
