"""Game session manager service for UC4 Game Session Management"""
from datetime import datetime
from config.db import get_connection, execute_query, insert
from models import (
    GamingSession, GameRecord, PauseRecord,
    SessionStatus, SessionEndReason, SessionParameters
)


class GameSessionManager:
    _active_sessions: dict = {}  # gambler_id -> GamingSession

    def _persist_game_record(self, conn, gr: GameRecord):
        gr.id = insert(conn,
            """INSERT INTO game_records
               (session_id, gambler_id, game_number, bet_amount, outcome,
                payout, stake_before, stake_after, duration_seconds, played_at)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (gr.session_id, gr.gambler_id, gr.game_number, gr.bet_amount,
             gr.outcome, gr.payout, gr.stake_before, gr.stake_after,
             gr.duration_sec, gr.played_at))

    def _persist_pause_record(self, conn, pr: PauseRecord):
        pr.id = insert(conn,
            """INSERT INTO pause_records
               (session_id, pause_reason, paused_at, resumed_at, duration_seconds)
               VALUES (%s,%s,%s,%s,%s)""",
            (pr.session_id, pr.reason, pr.paused_at,
             pr.resumed_at, pr.duration))

    def _update_session_db(self, conn, gs: GamingSession):
        execute_query(conn,
            """UPDATE game_sessions
               SET status=%s, final_stake=%s, total_games=%s,
                   total_wins=%s, total_losses=%s,
                   active_duration_seconds=%s, ended_at=%s
               WHERE id=%s""",
            (gs.status.value, gs.current_stake, gs.total_games,
             gs.wins, gs.losses,
             int(gs.active_duration),
             datetime.now() if gs.status not in
                 (SessionStatus.ACTIVE, SessionStatus.PAUSED) else None,
             gs.session_id))

    # ── 1. Start new session ──────────────────
    def start_new_session(self, gambler_id: int,
                          initial_stake: float,
                          params: SessionParameters) -> GamingSession:
        if gambler_id in self._active_sessions:
            existing = self._active_sessions[gambler_id]
            if existing.status in (SessionStatus.ACTIVE, SessionStatus.PAUSED):
                raise RuntimeError(
                    f"Gambler {gambler_id} already has an active session "
                    f"id={existing.session_id}")

        if not (params.lower_limit < initial_stake < params.upper_limit):
            raise ValueError("Initial stake must be between lower and upper limits")

        conn = get_connection()
        try:
            session_id = insert(conn,
                """INSERT INTO game_sessions
                   (gambler_id, status, initial_stake, upper_limit, lower_limit,
                    min_bet, max_bet, win_probability, started_at)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (gambler_id, SessionStatus.ACTIVE.value, initial_stake,
                 params.upper_limit, params.lower_limit,
                 params.min_bet, params.max_bet,
                 params.win_probability, datetime.now()))

            execute_query(conn,
                "UPDATE gamblers SET current_stake=%s WHERE id=%s",
                (initial_stake, gambler_id))

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

        gs = GamingSession(session_id, gambler_id, params, initial_stake)
        self._active_sessions[gambler_id] = gs
        print(f"[SESSION START] id={session_id}, gambler={gambler_id}, "
              f"stake={initial_stake:.2f}")
        return gs

    # ── 2. Continue session (play N games) ────
    def continue_session(self, gambler_id: int,
                         bet_amount: float, n_games: int = 1):
        gs = self._active_sessions.get(gambler_id)
        if not gs:
            raise RuntimeError(f"No active session for gambler {gambler_id}")

        for _ in range(n_games):
            if gs.status != SessionStatus.ACTIVE:
                break

            gr = gs.play_one_game(bet_amount)

            conn = get_connection()
            try:
                self._persist_game_record(conn, gr)
                execute_query(conn,
                    "UPDATE gamblers SET current_stake=%s WHERE id=%s",
                    (gs.current_stake, gambler_id))
                self._update_session_db(conn, gs)
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

            end_reason = gs._check_boundaries()
            if end_reason:
                self.end_session(gambler_id, end_reason)
                break

        return gs

    # ── 3. Pause ──────────────────────────────
    def pause_session(self, gambler_id: int, reason: str = "") -> PauseRecord:
        gs = self._active_sessions.get(gambler_id)
        if not gs:
            raise RuntimeError(f"No active session for gambler {gambler_id}")
        pr = gs.pause(reason)
        conn = get_connection()
        try:
            self._persist_pause_record(conn, pr)
            self._update_session_db(conn, gs)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        print(f"[SESSION PAUSED] gambler={gambler_id} reason='{reason}'")
        return pr

    # ── Resume ────────────────────────────────
    def resume_session(self, gambler_id: int):
        gs = self._active_sessions.get(gambler_id)
        if not gs:
            raise RuntimeError(f"No active session for gambler {gambler_id}")
        gs.resume()
        # Update last pause record with resume time
        if gs.pause_records:
            last = gs.pause_records[-1]
            conn = get_connection()
            try:
                execute_query(conn,
                    """UPDATE pause_records
                       SET resumed_at=%s, duration_seconds=%s
                       WHERE id=%s""",
                    (last.resumed_at, last.duration, last.id))
                self._update_session_db(conn, gs)
                conn.commit()
            finally:
                conn.close()
        print(f"[SESSION RESUMED] gambler={gambler_id}")

    # ── 4/5. End session ──────────────────────
    def end_session(self, gambler_id: int,
                    reason: SessionEndReason = SessionEndReason.MANUAL) -> dict:
        gs = self._active_sessions.get(gambler_id)
        if not gs:
            raise RuntimeError(f"No active session for gambler {gambler_id}")
        gs.end(reason)

        conn = get_connection()
        try:
            self._update_session_db(conn, gs)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

        del self._active_sessions[gambler_id]
        summary = gs.summary()
        print(f"[SESSION ENDED] Reason={reason.value} Summary={summary}")
        return summary

    def get_session(self, gambler_id: int) -> GamingSession:
        return self._active_sessions.get(gambler_id)
from datetime import datetime
from config.db import get_connection, execute_query, execute_one, insert
from models import GamingSession, GameRecord, PauseRecord, SessionParameters
from models.session_enums import SessionStatus, SessionEndReason


class GameSessionManager:
    _active_sessions: dict = {}  # gambler_id -> GamingSession

    def _persist_game_record(self, conn, gr: GameRecord):
        gr.id = insert(conn,
            """INSERT INTO game_records
               (session_id, gambler_id, game_number, bet_amount, outcome,
                payout, stake_before, stake_after, duration_seconds, played_at)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (gr.session_id, gr.gambler_id, gr.game_number, gr.bet_amount,
             gr.outcome, gr.payout, gr.stake_before, gr.stake_after,
             gr.duration_sec, gr.played_at))

    def _persist_pause_record(self, conn, pr: PauseRecord):
        pr.id = insert(conn,
            """INSERT INTO pause_records
               (session_id, pause_reason, paused_at, resumed_at, duration_seconds)
               VALUES (%s,%s,%s,%s,%s)""",
            (pr.session_id, pr.reason, pr.paused_at,
             pr.resumed_at, pr.duration))

    def _update_session_db(self, conn, gs: GamingSession):
        execute_query(conn,
            """UPDATE game_sessions
               SET status=%s, final_stake=%s, total_games=%s,
                   total_wins=%s, total_losses=%s,
                   active_duration_seconds=%s, ended_at=%s
               WHERE id=%s""",
            (gs.status.value, gs.current_stake, gs.total_games,
             gs.wins, gs.losses,
             int(gs.active_duration),
             datetime.now() if gs.status not in
                 (SessionStatus.ACTIVE, SessionStatus.PAUSED) else None,
             gs.session_id))

    # ── 1. Start new session ──────────────────
    def start_new_session(self, gambler_id: int,
                          initial_stake: float,
                          params: SessionParameters) -> GamingSession:
        if gambler_id in self._active_sessions:
            existing = self._active_sessions[gambler_id]
            if existing.status in (SessionStatus.ACTIVE, SessionStatus.PAUSED):
                raise RuntimeError(
                    f"Gambler {gambler_id} already has an active session "
                    f"id={existing.session_id}")

        if not (params.lower_limit < initial_stake < params.upper_limit):
            raise ValueError("Initial stake must be between lower and upper limits")

        conn = get_connection()
        try:
            session_id = insert(conn,
                """INSERT INTO game_sessions
                   (gambler_id, status, initial_stake, upper_limit, lower_limit,
                    min_bet, max_bet, win_probability, started_at)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (gambler_id, SessionStatus.ACTIVE.value, initial_stake,
                 params.upper_limit, params.lower_limit,
                 params.min_bet, params.max_bet,
                 params.win_probability, datetime.now()))

            execute_query(conn,
                "UPDATE gamblers SET current_stake=%s WHERE id=%s",
                (initial_stake, gambler_id))

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

        gs = GamingSession(session_id, gambler_id, params, initial_stake)
        self._active_sessions[gambler_id] = gs
        print(f"[SESSION START] id={session_id}, gambler={gambler_id}, "
              f"stake={initial_stake:.2f}")
        return gs

    # ── 2. Continue session (play N games) ────
    def continue_session(self, gambler_id: int,
                         bet_amount: float, n_games: int = 1):
        gs = self._active_sessions.get(gambler_id)
        if not gs:
            raise RuntimeError(f"No active session for gambler {gambler_id}")

        for _ in range(n_games):
            if gs.status != SessionStatus.ACTIVE:
                break

            gr = gs.play_one_game(bet_amount)

            conn = get_connection()
            try:
                self._persist_game_record(conn, gr)
                execute_query(conn,
                    "UPDATE gamblers SET current_stake=%s WHERE id=%s",
                    (gs.current_stake, gambler_id))
                self._update_session_db(conn, gs)
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

            end_reason = gs._check_boundaries()
            if end_reason:
                self.end_session(gambler_id, end_reason)
                break

        return gs

    # ── 3. Pause ──────────────────────────────
    def pause_session(self, gambler_id: int, reason: str = "") -> PauseRecord:
        gs = self._active_sessions.get(gambler_id)
        if not gs:
            raise RuntimeError(f"No active session for gambler {gambler_id}")
        pr = gs.pause(reason)
        conn = get_connection()
        try:
            self._persist_pause_record(conn, pr)
            self._update_session_db(conn, gs)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        print(f"[SESSION PAUSED] gambler={gambler_id} reason='{reason}'")
        return pr

    # ── Resume ────────────────────────────────
    def resume_session(self, gambler_id: int):
        gs = self._active_sessions.get(gambler_id)
        if not gs:
            raise RuntimeError(f"No active session for gambler {gambler_id}")
        gs.resume()
        # Update last pause record with resume time
        if gs.pause_records:
            last = gs.pause_records[-1]
            conn = get_connection()
            try:
                execute_query(conn,
                    """UPDATE pause_records
                       SET resumed_at=%s, duration_seconds=%s
                       WHERE id=%s""",
                    (last.resumed_at, last.duration, last.id))
                self._update_session_db(conn, gs)
                conn.commit()
            finally:
                conn.close()
        print(f"[SESSION RESUMED] gambler={gambler_id}")

    # ── 4/5. End session ──────────────────────
    def end_session(self, gambler_id: int,
                    reason: SessionEndReason = SessionEndReason.MANUAL) -> dict:
        gs = self._active_sessions.get(gambler_id)
        if not gs:
            raise RuntimeError(f"No active session for gambler {gambler_id}")
        gs.end(reason)

        conn = get_connection()
        try:
            self._update_session_db(conn, gs)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

        del self._active_sessions[gambler_id]
        summary = gs.summary()
        print(f"[SESSION ENDED] Reason={reason.value} Summary={summary}")
        return summary

    def get_session(self, gambler_id: int) -> GamingSession:
        return self._active_sessions.get(gambler_id)
