"""Win/Loss calculator service for UC5 Win/Loss Calculation"""
from config.db import get_connection, execute_query, insert
from models import (
    GameResult, WinLossStatistics, RunningTotals,
    RandomOutcomeStrategy, OddsConfig, OddsType
)


class WinLossCalculator:
    def __init__(self, session_id: int, gambler_id: int,
                 initial_balance: float,
                 outcome_strategy=None,
                 odds_config: OddsConfig = None):
        self.session_id       = session_id
        self.gambler_id       = gambler_id
        self.stats            = WinLossStatistics()
        self.totals           = RunningTotals(initial_balance)
        self.outcome_strategy = outcome_strategy or RandomOutcomeStrategy()
        self.odds_config      = odds_config or OddsConfig(OddsType.FIXED, 2.0)
        self._game_counter    = 0
        self._stats_row_id    = None
        self._init_db()

    def _init_db(self):
        conn = get_connection()
        try:
            self._stats_row_id = insert(conn,
                """INSERT INTO win_loss_statistics
                   (session_id, gambler_id) VALUES (%s,%s)""",
                (self.session_id, self.gambler_id))
            conn.commit()
        finally:
            conn.close()

    # ── 1. Determine outcome ─────────────────
    def determine_outcome(self, win_probability: float) -> bool:
        return self.outcome_strategy.determine(win_probability)

    # ── 2. Calculate winnings ─────────────────
    def calculate_winnings(self, bet_amount: float,
                           win_probability: float = 0.5) -> float:
        return self.odds_config.calculate_payout(bet_amount, win_probability)

    # ── 3. Calculate losses ───────────────────
    def calculate_loss(self, bet_amount: float) -> float:
        return float(bet_amount)  # full bet amount is the loss

    # ── 4. Play one game (maintains running totals) ──
    def play_game(self, bet_amount: float,
                  win_probability: float = 0.5) -> GameResult:
        self._game_counter += 1
        stake_before = self.totals.current_balance

        result = GameResult(self.session_id, self.gambler_id,
                            self._game_counter, bet_amount,
                            win_probability, self.odds_config, stake_before)
        won = self.determine_outcome(win_probability)
        result.resolve(won)

        # Update in-memory state
        self.stats.record(result)
        self.totals.update(result)

        # Persist running total snapshot
        conn = get_connection()
        try:
            insert(conn,
                """INSERT INTO running_totals
                   (session_id, gambler_id, game_number,
                    cumulative_winnings, cumulative_losses,
                    net_profit_loss, balance_snapshot)
                   VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (self.session_id, self.gambler_id,
                 self._game_counter,
                 self.totals.cumulative_winnings,
                 self.totals.cumulative_losses,
                 self.totals.net_profit_loss,
                 result.stake_after))

            # Update stats table
            execute_query(conn,
                """UPDATE win_loss_statistics SET
                   total_wins=%s, total_losses=%s, total_pushes=%s,
                   total_winnings=%s, total_losses_amount=%s,
                   largest_win=%s, largest_loss=%s,
                   current_win_streak=%s, current_loss_streak=%s,
                   longest_win_streak=%s, longest_loss_streak=%s
                   WHERE id=%s""",
                (self.stats.total_wins, self.stats.total_losses,
                 self.stats.total_pushes,
                 self.stats.total_winnings, self.stats.total_losses_amount,
                 self.stats.largest_win, self.stats.largest_loss,
                 self.stats.current_win_streak, self.stats.current_loss_streak,
                 self.stats.longest_win_streak, self.stats.longest_loss_streak,
                 self._stats_row_id))

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

        return result

    # ── 5. Compute win/loss ratio ─────────────
    def get_win_loss_ratio(self) -> dict:
        return {
            "win_rate_%":    round(self.stats.win_rate, 2),
            "win_loss_ratio": round(self.stats.win_loss_ratio, 4),
            "profit_factor":  round(self.stats.profit_factor, 4),
        }

    # ── 6. Track consecutive streaks ──────────
    def get_streak_info(self) -> dict:
        return {
            "current_win_streak":  self.stats.current_win_streak,
            "current_loss_streak": self.stats.current_loss_streak,
            "longest_win_streak":  self.stats.longest_win_streak,
            "longest_loss_streak": self.stats.longest_loss_streak,
        }

    def full_report(self) -> dict:
        d = self.stats.to_dict()
        d["net_profit_loss"]      = self.totals.net_profit_loss
        d["cumulative_winnings"]  = round(self.totals.cumulative_winnings, 2)
        d["cumulative_losses"]    = round(self.totals.cumulative_losses, 2)
        d["current_balance"]      = round(self.totals.current_balance, 2)
        return d
