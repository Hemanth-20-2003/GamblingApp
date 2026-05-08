"""
Interactive Menu - UC7 User Interaction
Handles user interactions for creating gamblers, managing sessions, placing bets, etc.
"""

import time
from config.db import get_connection, execute_one

from service import (
    GamblerProfileService, StakeManagementService, BettingService,
    GameSessionManager, WinLossCalculator, InputValidator, SafeInputHandler
)
from models import (
    SessionParameters, SessionEndReason, OddsType, OddsConfig, 
    WeightedProbabilityStrategy, ValidationConfig
)
from .game_status_display import GameStatusDisplay


class InteractiveMenu:
    def __init__(self):
        self.profile_svc  = GamblerProfileService()
        self.stake_svc    = StakeManagementService()
        self.betting_svc  = BettingService()
        self.session_mgr  = GameSessionManager()
        self.display      = GameStatusDisplay()
        self.validator_cfg = ValidationConfig()
        self.gambler_id   = None
        self.calc         = None  # WinLossCalculator for active session

    # ── helpers ──────────────────────────────
    def _require_login(self):
        if not self.gambler_id:
            print("  ⚠ Please login / create a gambler first (Option 1).")
            return False
        return True

    def _require_session(self):
        if not self._require_login():
            return False
        gs = self.session_mgr.get_session(self.gambler_id)
        if not gs:
            print("  ⚠ No active session. Start one first (Option 3).")
            return False
        return True

    def _input(self, prompt, default=None):
        raw = input(f"  {prompt}").strip()
        return raw if raw else default

    def _float_input(self, prompt, default=None):
        validator = InputValidator(config=self.validator_cfg,
                                   gambler_id=self.gambler_id)
        handler   = SafeInputHandler(validator)
        raw = input(f"  {prompt}").strip()
        if not raw and default is not None:
            return default
        val, r = validator.parse_and_validate_numeric(raw, "input")
        if val is None:
            print(r.report())
            return default
        return val

    # ── menu options ──────────────────────────

    def menu_create_gambler(self):
        GameStatusDisplay.header("CREATE GAMBLER")
        name  = self._input("Name: ", "Player1")
        email = self._input("Email: ", "player@example.com")
        stake = self._float_input("Initial Stake: ", 500.0)
        win_t = self._float_input("Win Threshold (e.g. 1000): ", 1000.0)
        los_t = self._float_input("Loss Threshold (e.g. 100): ", 100.0)
        try:
            p = self.profile_svc.create_gambler(name, email, stake, win_t, los_t)
            self.gambler_id = p.id
            print(f"\n  ✓ Gambler created. id={p.id}")
        except Exception as e:
            print(f"\n  ✗ Error: {e}")

    def menu_login(self):
        GameStatusDisplay.header("LOGIN")
        gid = self._float_input("Enter Gambler ID: ", None)
        if gid is None:
            return
        conn = get_connection()
        try:
            row = execute_one(conn, "SELECT id,name FROM gamblers WHERE id=%s",
                              (int(gid),))
        finally:
            conn.close()
        if row:
            self.gambler_id = int(gid)
            print(f"\n  ✓ Logged in as '{row['name']}' (id={self.gambler_id})")
        else:
            print(f"\n  ✗ Gambler id={int(gid)} not found")

    def menu_view_status(self):
        if not self._require_login():
            return
        GameStatusDisplay.header("CURRENT STATUS")
        self.display.display_current_status(self.gambler_id)

    def menu_start_session(self):
        if not self._require_login():
            return
        GameStatusDisplay.header("START SESSION")
        stake = self._float_input("Initial Stake: ", 500.0)
        upper = self._float_input("Win Limit (upper): ", 1000.0)
        lower = self._float_input("Loss Limit (lower): ", 100.0)
        min_b = self._float_input("Min Bet: ", 5.0)
        max_b = self._float_input("Max Bet: ", 200.0)
        prob  = self._float_input("Win Probability (0-1): ", 0.50)

        v = InputValidator(config=self.validator_cfg,
                           gambler_id=self.gambler_id)
        r = v.validate_all(stake, upper_limit=upper,
                           lower_limit=lower, probability=prob)
        if not r.is_valid:
            print(r.report())
            return

        params = SessionParameters(upper, lower, min_b, max_b,
                                   win_probability=prob)
        try:
            gs = self.session_mgr.start_new_session(self.gambler_id, stake, params)
            self.calc = WinLossCalculator(
                gs.session_id, self.gambler_id, stake,
                outcome_strategy=WeightedProbabilityStrategy(0.01),
                odds_config=OddsConfig(OddsType.FIXED, 2.0))
            print(f"\n  ✓ Session started (id={gs.session_id})")
        except Exception as e:
            print(f"\n  ✗ Error: {e}")

    def menu_place_bet(self):
        if not self._require_session():
            return
        GameStatusDisplay.header("PLACE BET")
        self.display.display_current_status(self.gambler_id)

        gs      = self.session_mgr.get_session(self.gambler_id)
        bet_amt = self._float_input(
            f"Bet amount (current stake ₹{gs.current_stake:.2f}): ",
            min(50.0, gs.current_stake))

        v = InputValidator(config=self.validator_cfg,
                           gambler_id=self.gambler_id)
        r = v.validate_bet_amount(bet_amt, gs.current_stake)
        if not r.is_valid:
            print(r.report())
            return

        try:
            result = self.calc.play_game(bet_amt, gs.params.win_probability)
            gs.current_stake = result.stake_after  # sync in-memory
            # Persist game record manually
            conn = get_connection()
            try:
                from config.db import insert as db_insert
                db_insert(conn,
                    """INSERT INTO game_records
                       (session_id, gambler_id, game_number, bet_amount,
                        outcome, payout, stake_before, stake_after, played_at)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (gs.session_id, self.gambler_id, result.game_number,
                     result.bet_amount, result.outcome,
                     max(result.net_change, 0),
                     result.stake_before, result.stake_after,
                     result.played_at))
                from config.db import execute_query as db_exec
                db_exec(conn,
                    "UPDATE game_sessions SET total_games=%s WHERE id=%s",
                    (result.game_number, gs.session_id))
                db_exec(conn,
                    "UPDATE gamblers SET current_stake=%s WHERE id=%s",
                    (result.stake_after, self.gambler_id))
                conn.commit()
            finally:
                conn.close()

            self.display.display_game_outcome(
                result.game_number, result.outcome,
                result.bet_amount,
                max(result.net_change, 0),
                result.stake_before, result.stake_after)

            # Check limits
            if result.stake_after >= gs.params.upper_limit:
                print("\n  🏆 WIN THRESHOLD REACHED!")
                summary = self.session_mgr.end_session(
                    self.gambler_id, SessionEndReason.UPPER_LIMIT)
                self.display.display_session_summary(summary)
            elif result.stake_after <= gs.params.lower_limit:
                print("\n  💸 LOSS THRESHOLD REACHED!")
                summary = self.session_mgr.end_session(
                    self.gambler_id, SessionEndReason.LOWER_LIMIT)
                self.display.display_session_summary(summary)
        except Exception as e:
            print(f"\n  ✗ Error: {e}")

    def menu_auto_play(self):
        if not self._require_session():
            return
        GameStatusDisplay.header("AUTO-PLAY")
        n   = int(self._float_input("Number of auto games: ", 10))
        bet = self._float_input("Bet per game: ", 20.0)
        gs  = self.session_mgr.get_session(self.gambler_id)
        print(f"\n  Running {n} games...")
        for i in range(n):
            if gs.current_stake < bet:
                print("  ⚠ Insufficient stake to continue")
                break
            result = self.calc.play_game(bet, gs.params.win_probability)
            gs.current_stake = result.stake_after
            self.display.display_game_outcome(
                result.game_number, result.outcome,
                result.bet_amount, max(result.net_change, 0),
                result.stake_before, result.stake_after)
            time.sleep(0.05)
            if result.stake_after >= gs.params.upper_limit:
                print("  🏆 WIN LIMIT HIT — ending session.")
                summary = self.session_mgr.end_session(
                    self.gambler_id, SessionEndReason.UPPER_LIMIT)
                self.display.display_session_summary(summary)
                return
            if result.stake_after <= gs.params.lower_limit:
                print("  💸 LOSS LIMIT HIT — ending session.")
                summary = self.session_mgr.end_session(
                    self.gambler_id, SessionEndReason.LOWER_LIMIT)
                self.display.display_session_summary(summary)
                return
        if self.calc:
            print("\n  Win/Loss Report:")
            for k, v in self.calc.full_report().items():
                print(f"    {k:<25}: {v}")

    def menu_pause_session(self):
        if not self._require_session():
            return
        reason = self._input("Pause reason: ", "Manual pause")
        self.session_mgr.pause_session(self.gambler_id, reason)
        input("  [Press Enter to resume]")
        self.session_mgr.resume_session(self.gambler_id)
        print("  ✓ Session resumed")

    def menu_end_session(self):
        if not self._require_session():
            return
        confirm = self._input("End session? (y/n): ", "n")
        if confirm.lower() != "y":
            return
        summary = self.session_mgr.end_session(
            self.gambler_id, SessionEndReason.MANUAL)
        self.display.display_session_summary(summary)
        self.calc = None

    def menu_win_loss_report(self):
        if not self._require_login() or not self.calc:
            print("  No active Win/Loss calculator. Play some games first.")
            return
        GameStatusDisplay.header("WIN/LOSS REPORT")
        for k, v in self.calc.full_report().items():
            if isinstance(v, float):
                print(f"  {k:<25}: {v:,.4f}")
            else:
                print(f"  {k:<25}: {v}")

    # ── Main menu loop ────────────────────────
    def run(self):
        GameStatusDisplay.header("WELCOME TO GAMBLING APP")
        print("  Manual MySQL connection  |  No ORM\n")

        menu = [
            ("1", "Create new gambler",   self.menu_create_gambler),
            ("2", "Login (existing)",     self.menu_login),
            ("3", "View status",          self.menu_view_status),
            ("4", "Start session",        self.menu_start_session),
            ("5", "Place a bet",          self.menu_place_bet),
            ("6", "Auto-play N games",    self.menu_auto_play),
            ("7", "Pause / Resume",       self.menu_pause_session),
            ("8", "End session",          self.menu_end_session),
            ("9", "Win/Loss report",      self.menu_win_loss_report),
            ("0", "Exit",                 None),
        ]

        while True:
            print("\n")
            for key, label, _ in menu:
                marker = "  " if key != "0" else "  "
                print(f"{marker} [{key}] {label}")
            if self.gambler_id:
                print(f"\n  Logged in as gambler id={self.gambler_id}")

            choice = self._input("\n  Select option: ", "0")

            if choice == "0":
                print("\n  Goodbye! Final session ended cleanly.\n")
                if self.gambler_id and \
                        self.session_mgr.get_session(self.gambler_id):
                    self.session_mgr.end_session(
                        self.gambler_id, SessionEndReason.MANUAL)
                break

            matched = False
            for key, _, fn in menu:
                if choice == key and fn:
                    matched = True
                    fn()
                    break
            if not matched and choice != "0":
                print("  ✗ Invalid option")
