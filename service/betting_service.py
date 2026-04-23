import random
from config.db import get_connection, execute_query, execute_one, insert
from models import Bet, BettingSession
from models.betting_strategy import STRATEGIES


class BettingService:

    def _get_stake(self, conn, gambler_id):
        row = execute_one(conn, "SELECT current_stake FROM gamblers WHERE id=%s",
                          (gambler_id,))
        if not row:
            raise ValueError(f"Gambler {gambler_id} not found")
        return float(row["current_stake"])

    def _get_prefs(self, conn, gambler_id):
        return execute_one(conn,
            "SELECT * FROM betting_preferences WHERE gambler_id=%s", (gambler_id,))

    def _save_bet(self, conn, bet: Bet) -> int:
        return insert(conn,
            """INSERT INTO bets
               (gambler_id, session_id, strategy, bet_amount, win_probability,
                odds, potential_win, outcome, actual_payout,
                stake_before, stake_after, placed_at, settled_at)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (bet.gambler_id, bet.session_id, bet.strategy, bet.bet_amount,
             bet.win_probability, bet.odds, bet.potential_win, bet.outcome,
             bet.actual_payout, bet.stake_before, bet.stake_after,
             bet.placed_at, bet.settled_at))

    def _update_stake(self, conn, gambler_id, new_stake):
        execute_query(conn,
            "UPDATE gamblers SET current_stake=%s WHERE id=%s",
            (new_stake, gambler_id))

    # ── 1. Place single bet ───────────────────
    def place_bet(self, gambler_id: int, amount: float,
                  win_probability: float = 0.5, odds: float = 2.0,
                  session_id: int = None, strategy: str = "FIXED") -> Bet:
        conn = get_connection()
        try:
            stake = self._get_stake(conn, gambler_id)
            prefs = self._get_prefs(conn, gambler_id)

            # Validate
            if amount <= 0:
                raise ValueError("Bet amount must be positive")
            if amount > stake:
                raise ValueError(f"Bet {amount:.2f} exceeds stake {stake:.2f}")
            if prefs:
                if amount < float(prefs["min_bet"]):
                    raise ValueError(f"Bet below minimum {prefs['min_bet']}")
                if amount > float(prefs["max_bet"]):
                    raise ValueError(f"Bet above maximum {prefs['max_bet']}")

            bet = Bet(gambler_id, session_id, strategy,
                      amount, win_probability, odds, stake)
            bet.id = self._save_bet(conn, bet)
            conn.commit()
            print(f"[BET PLACED] id={bet.id} amount={amount:.2f}")
            return bet
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ── 2. Determine outcome ─────────────────
    def determine_outcome(self, win_probability: float) -> bool:
        """Return True for WIN based on probability."""
        if not 0 < win_probability < 1:
            raise ValueError("Probability must be between 0 and 1 (exclusive)")
        return random.random() < win_probability

    # ── 3. Settle bet (apply to stake) ────────
    def settle_bet(self, bet: Bet, won: bool) -> Bet:
        bet.settle(won)
        conn = get_connection()
        try:
            self._update_stake(conn, bet.gambler_id, bet.stake_after)
            execute_query(conn,
                """UPDATE bets SET outcome=%s, actual_payout=%s,
                          stake_after=%s, settled_at=%s
                   WHERE id=%s""",
                (bet.outcome, bet.actual_payout, bet.stake_after,
                 bet.settled_at, bet.id))
            conn.commit()
            print(f"[BET SETTLED] {bet}")
            return bet
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ── 4. Validate bet amount ────────────────
    def validate_bet_amount(self, gambler_id: int, amount: float) -> dict:
        conn = get_connection()
        try:
            stake = self._get_stake(conn, gambler_id)
            prefs = self._get_prefs(conn, gambler_id)
            errors = []
            if amount <= 0:
                errors.append("Amount must be positive")
            if amount > stake:
                errors.append(f"Amount {amount:.2f} exceeds stake {stake:.2f}")
            if prefs:
                if amount < float(prefs["min_bet"]):
                    errors.append(f"Below min bet {prefs['min_bet']}")
                if amount > float(prefs["max_bet"]):
                    errors.append(f"Above max bet {prefs['max_bet']}")
            return {"valid": len(errors) == 0, "errors": errors, "stake": stake}
        finally:
            conn.close()

    # ── 5. Bet with strategy ──────────────────
    def place_bet_with_strategy(self, gambler_id: int, strategy_name: str,
                                base_bet: float, win_probability: float = 0.5,
                                odds: float = 2.0, session_id: int = None,
                                last_bet: float = 0.0, last_won: bool = True) -> Bet:
        cls = STRATEGIES.get(strategy_name.upper())
        if not cls:
            raise ValueError(f"Unknown strategy '{strategy_name}'. "
                             f"Available: {list(STRATEGIES.keys())}")
        strategy = cls() if strategy_name.upper() in ("FIBONACCI",) else cls(base_bet) \
            if strategy_name.upper() in ("FIXED",) else \
            cls(5.0) if strategy_name.upper() == "PERCENTAGE" else cls()

        conn = get_connection()
        try:
            stake = self._get_stake(conn, gambler_id)
        finally:
            conn.close()

        amount = strategy.calculate_bet(stake, last_bet, last_won, base_bet)
        amount = max(0.01, round(amount, 2))
        return self.place_bet(gambler_id, amount, win_probability,
                              odds, session_id, strategy_name)

    # ── 6. Multiple consecutive bets ──────────
    def place_consecutive_bets(self, gambler_id: int, count: int,
                               bet_amount: float, win_probability: float = 0.5,
                               odds: float = 2.0, session_id: int = None,
                               strategy: str = "FIXED") -> BettingSession:
        bs = BettingSession(gambler_id, session_id)
        for i in range(count):
            conn = get_connection()
            try:
                stake = self._get_stake(conn, gambler_id)
            finally:
                conn.close()

            if stake < bet_amount:
                print(f"[CONSECUTIVE] Stopping at bet {i+1}: insufficient stake")
                break

            bet = self.place_bet(gambler_id, bet_amount, win_probability,
                                 odds, session_id, strategy)
            won = self.determine_outcome(win_probability)
            self.settle_bet(bet, won)
            bs.add_bet(bet)

        print(f"[CONSECUTIVE BETS] Summary: {bs.summary()}")
        return bs
