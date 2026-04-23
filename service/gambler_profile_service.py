from config.db import get_connection, execute_query, execute_one, insert
from models import GamblerProfile, BettingPreferences, GamblerStatisticsDTO

MIN_STAKE = 10.0


class GamblerProfileService:

    # ── 1. Create ────────────────────────────
    def create_gambler(self, name: str, email: str, initial_stake: float,
                       win_threshold: float, loss_threshold: float) -> GamblerProfile:
        """Validate and persist a new gambler + default preferences + empty stats."""
        # Validation
        if initial_stake < MIN_STAKE:
            raise ValueError(f"Initial stake {initial_stake} is below minimum {MIN_STAKE}")
        if win_threshold <= initial_stake:
            raise ValueError("Win threshold must be greater than initial stake")
        if loss_threshold >= initial_stake:
            raise ValueError("Loss threshold must be less than initial stake")
        if loss_threshold < 0:
            raise ValueError("Loss threshold cannot be negative")

        profile = GamblerProfile(name, email, initial_stake, win_threshold, loss_threshold)

        conn = get_connection()
        try:
            # Insert gambler
            profile.id = insert(conn,
                """INSERT INTO gamblers (name, email, initial_stake, current_stake,
                        win_threshold, loss_threshold, is_active, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (name, email, initial_stake, initial_stake,
                 win_threshold, loss_threshold, True, profile.created_at))

            # Default betting preferences
            insert(conn,
                """INSERT INTO betting_preferences (gambler_id) VALUES (%s)""",
                (profile.id,))

            # Empty statistics row
            insert(conn,
                """INSERT INTO gambler_statistics (gambler_id) VALUES (%s)""",
                (profile.id,))

            conn.commit()
            print(f"[CREATE] Gambler '{name}' created with id={profile.id}")
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

        return profile

    # ── 2. Update ────────────────────────────
    def update_gambler(self, gambler_id: int, **kwargs) -> bool:
        """
        Update personal info or preferences.
        Supported keys: name, email, win_threshold, loss_threshold,
                        min_bet, max_bet, preferred_strategy, auto_play, session_limit
        """
        gambler_fields = {k: v for k, v in kwargs.items()
                          if k in ("name", "email", "win_threshold", "loss_threshold")}
        pref_fields    = {k: v for k, v in kwargs.items()
                          if k in ("min_bet", "max_bet", "preferred_strategy",
                                   "auto_play", "session_limit")}

        conn = get_connection()
        try:
            if gambler_fields:
                sets = ", ".join(f"{k}=%s" for k in gambler_fields)
                vals = list(gambler_fields.values()) + [gambler_id]
                execute_query(conn, f"UPDATE gamblers SET {sets} WHERE id=%s", vals)

            if pref_fields:
                sets = ", ".join(f"{k}=%s" for k in pref_fields)
                vals = list(pref_fields.values()) + [gambler_id]
                execute_query(conn,
                    f"UPDATE betting_preferences SET {sets} WHERE gambler_id=%s", vals)

            conn.commit()
            print(f"[UPDATE] Gambler id={gambler_id} updated: {kwargs}")
            return True
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ── 3. Retrieve ───────────────────────────
    def retrieve_gambler(self, gambler_id: int):
        """Return (GamblerProfile, BettingPreferences, GamblerStatisticsDTO) tuple."""
        conn = get_connection()
        try:
            g_row = execute_one(conn,
                "SELECT * FROM gamblers WHERE id=%s", (gambler_id,))
            if not g_row:
                raise ValueError(f"Gambler id={gambler_id} not found")

            p_row = execute_one(conn,
                "SELECT * FROM betting_preferences WHERE gambler_id=%s", (gambler_id,))

            s_row = execute_one(conn,
                "SELECT * FROM gambler_statistics WHERE gambler_id=%s", (gambler_id,))

            profile = GamblerProfile(
                g_row["name"], g_row["email"],
                g_row["initial_stake"], g_row["win_threshold"], g_row["loss_threshold"])
            profile.id = g_row["id"]
            profile.current_stake = float(g_row["current_stake"])
            profile.is_active = bool(g_row["is_active"])

            prefs = BettingPreferences(
                gambler_id,
                p_row["min_bet"], p_row["max_bet"],
                p_row["preferred_strategy"], bool(p_row["auto_play"]),
                p_row["session_limit"]) if p_row else BettingPreferences(gambler_id)

            stats = GamblerStatisticsDTO(s_row) if s_row else GamblerStatisticsDTO(
                {"gambler_id": gambler_id})

            return profile, prefs, stats
        finally:
            conn.close()

    # ── 4. Validate eligibility ────────────────
    def validate_eligibility(self, gambler_id: int) -> dict:
        """Check if a gambler is eligible to play."""
        conn = get_connection()
        try:
            row = execute_one(conn,
                "SELECT * FROM gamblers WHERE id=%s", (gambler_id,))
            if not row:
                return {"eligible": False, "reason": "Gambler not found"}

            issues = []
            if not row["is_active"]:
                issues.append("Account is inactive")
            if float(row["current_stake"]) < MIN_STAKE:
                issues.append(f"Stake {row['current_stake']} below minimum {MIN_STAKE}")
            if float(row["current_stake"]) <= float(row["loss_threshold"]):
                issues.append("Stake at or below loss threshold")
            if float(row["current_stake"]) >= float(row["win_threshold"]):
                issues.append("Stake already at or above win threshold")

            return {"eligible": len(issues) == 0, "issues": issues}
        finally:
            conn.close()

    # ── 5. Reset ──────────────────────────────
    def reset_gambler(self, gambler_id: int, new_initial_stake: float = None) -> bool:
        """Reset gambler to initial state (or a new stake) for a fresh session."""
        conn = get_connection()
        try:
            row = execute_one(conn,
                "SELECT * FROM gamblers WHERE id=%s", (gambler_id,))
            if not row:
                raise ValueError(f"Gambler id={gambler_id} not found")

            stake = float(new_initial_stake) if new_initial_stake else float(row["initial_stake"])
            # Proportional threshold adjustment
            original = float(row["initial_stake"])
            ratio = stake / original if original else 1.0
            new_win  = float(row["win_threshold"])  * ratio
            new_loss = float(row["loss_threshold"]) * ratio

            execute_query(conn,
                """UPDATE gamblers SET current_stake=%s, initial_stake=%s,
                          win_threshold=%s, loss_threshold=%s, is_active=TRUE
                   WHERE id=%s""",
                (stake, stake, new_win, new_loss, gambler_id))

            # Reset statistics
            execute_query(conn,
                """UPDATE gambler_statistics
                   SET total_bets=0, total_wins=0, total_losses=0,
                       total_winnings=0, total_lost=0, largest_win=0, largest_loss=0
                   WHERE gambler_id=%s""", (gambler_id,))

            conn.commit()
            print(f"[RESET] Gambler id={gambler_id} reset. New stake={stake:.2f}")
            return True
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ── Helper: record a bet result on statistics ──
    def record_bet_result(self, gambler_id: int, won: bool, amount: float):
        conn = get_connection()
        try:
            if won:
                execute_query(conn,
                    """UPDATE gambler_statistics
                       SET total_bets=total_bets+1, total_wins=total_wins+1,
                           total_winnings=total_winnings+%s,
                           largest_win=GREATEST(largest_win, %s)
                       WHERE gambler_id=%s""", (amount, amount, gambler_id))
            else:
                execute_query(conn,
                    """UPDATE gambler_statistics
                       SET total_bets=total_bets+1, total_losses=total_losses+1,
                           total_lost=total_lost+%s,
                           largest_loss=GREATEST(largest_loss, %s)
                       WHERE gambler_id=%s""", (amount, amount, gambler_id))
            conn.commit()
        finally:
            conn.close()
