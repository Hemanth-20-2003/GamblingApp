"""Gaming session class for UC4 Game Session Management"""
import random
import time
from datetime import datetime
from models.session_enums import SessionStatus, SessionEndReason
from models.session_parameters import SessionParameters
from models.game_record import GameRecord
from models.pause_record import PauseRecord


class GamingSession:
    def __init__(self, session_id, gambler_id, params: SessionParameters,
                 initial_stake: float):
        self.session_id    = session_id
        self.gambler_id    = gambler_id
        self.params        = params
        self.current_stake = float(initial_stake)
        self.status        = SessionStatus.ACTIVE
        self.game_records: list[GameRecord] = []
        self.pause_records: list[PauseRecord] = []
        self.started_at    = datetime.now()
        self._active_seconds = 0.0
        self._segment_start  = time.time()
        self._current_pause: PauseRecord = None

    @property
    def total_games(self):
        return len(self.game_records)

    @property
    def wins(self):
        return sum(1 for g in self.game_records if g.outcome == "WIN")

    @property
    def losses(self):
        return sum(1 for g in self.game_records if g.outcome == "LOSS")

    @property
    def active_duration(self):
        if self.status == SessionStatus.ACTIVE:
            return self._active_seconds + (time.time() - self._segment_start)
        return self._active_seconds

    def _check_boundaries(self):
        if self.current_stake >= self.params.upper_limit:
            return SessionEndReason.UPPER_LIMIT
        if self.current_stake <= self.params.lower_limit:
            return SessionEndReason.LOWER_LIMIT
        if self.total_games >= self.params.max_games:
            return SessionEndReason.MAX_GAMES
        if self.active_duration >= self.params.max_duration_seconds:
            return SessionEndReason.TIMEOUT
        return None

    def play_one_game(self, bet_amount: float) -> GameRecord:
        if self.status != SessionStatus.ACTIVE:
            raise RuntimeError(f"Session not active (status={self.status.value})")

        t0 = time.time()
        won = random.random() < self.params.win_probability
        payout = bet_amount if won else 0.0
        stake_before = self.current_stake
        self.current_stake += payout - bet_amount
        duration = time.time() - t0

        gr = GameRecord(
            self.session_id, self.gambler_id,
            self.total_games + 1,
            bet_amount, "WIN" if won else "LOSS",
            payout, stake_before, self.current_stake)
        gr.duration_sec = round(duration, 3)
        self.game_records.append(gr)
        return gr

    def pause(self, reason=""):
        if self.status != SessionStatus.ACTIVE:
            raise RuntimeError("Only ACTIVE sessions can be paused")
        self._active_seconds += time.time() - self._segment_start
        self.status = SessionStatus.PAUSED
        pr = PauseRecord(self.session_id, reason)
        self._current_pause = pr
        self.pause_records.append(pr)
        return pr

    def resume(self):
        if self.status != SessionStatus.PAUSED:
            raise RuntimeError("Only PAUSED sessions can be resumed")
        self.status = SessionStatus.ACTIVE
        self._segment_start = time.time()
        if self._current_pause:
            self._current_pause.resumed_at = datetime.now()
            self._current_pause.duration = int(
                (self._current_pause.resumed_at -
                 self._current_pause.paused_at).total_seconds())
            self._current_pause = None

    def end(self, reason: SessionEndReason):
        if reason == SessionEndReason.UPPER_LIMIT:
            self.status = SessionStatus.ENDED_WIN
        elif reason == SessionEndReason.LOWER_LIMIT:
            self.status = SessionStatus.ENDED_LOSS
        elif reason == SessionEndReason.TIMEOUT:
            self.status = SessionStatus.ENDED_TIMEOUT
        else:
            self.status = SessionStatus.ENDED_MANUAL
        self._active_seconds += time.time() - self._segment_start

    def summary(self):
        return {
            "session_id":       self.session_id,
            "status":           self.status.value,
            "initial_stake":    self.params.upper_limit,  # stored in params
            "final_stake":      round(self.current_stake, 2),
            "total_games":      self.total_games,
            "wins":             self.wins,
            "losses":           self.losses,
            "win_rate":         round(self.wins / max(self.total_games, 1) * 100, 1),
            "active_seconds":   round(self.active_duration, 1),
        }
import time
from datetime import datetime
from .session_enums import SessionStatus, SessionEndReason


class GamingSession:
    def __init__(self, session_id, gambler_id, params,
                 initial_stake: float):
        self.session_id    = session_id
        self.gambler_id    = gambler_id
        self.params        = params
        self.current_stake = float(initial_stake)
        self.status        = SessionStatus.ACTIVE
        self.game_records: list = []
        self.pause_records: list = []
        self.started_at    = datetime.now()
        self._active_seconds = 0.0
        self._segment_start  = time.time()
        self._current_pause  = None

    @property
    def total_games(self):
        return len(self.game_records)

    @property
    def wins(self):
        return sum(1 for g in self.game_records if g.outcome == "WIN")

    @property
    def losses(self):
        return sum(1 for g in self.game_records if g.outcome == "LOSS")

    @property
    def active_duration(self):
        if self.status == SessionStatus.ACTIVE:
            return self._active_seconds + (time.time() - self._segment_start)
        return self._active_seconds

    def _check_boundaries(self):
        if self.current_stake >= self.params.upper_limit:
            return SessionEndReason.UPPER_LIMIT
        if self.current_stake <= self.params.lower_limit:
            return SessionEndReason.LOWER_LIMIT
        if self.total_games >= self.params.max_games:
            return SessionEndReason.MAX_GAMES
        if self.active_duration >= self.params.max_duration_seconds:
            return SessionEndReason.TIMEOUT
        return None

    def play_one_game(self, bet_amount: float):
        from .game_record import GameRecord
        
        if self.status != SessionStatus.ACTIVE:
            raise RuntimeError(f"Session not active (status={self.status.value})")

        import random
        t0 = time.time()
        won = random.random() < self.params.win_probability
        payout = bet_amount if won else 0.0
        stake_before = self.current_stake
        self.current_stake += payout - bet_amount
        duration = time.time() - t0

        gr = GameRecord(
            self.session_id, self.gambler_id,
            self.total_games + 1,
            bet_amount, "WIN" if won else "LOSS",
            payout, stake_before, self.current_stake)
        gr.duration_sec = round(duration, 3)
        self.game_records.append(gr)
        return gr

    def pause(self, reason=""):
        from .pause_record import PauseRecord
        
        if self.status != SessionStatus.ACTIVE:
            raise RuntimeError("Only ACTIVE sessions can be paused")
        self._active_seconds += time.time() - self._segment_start
        self.status = SessionStatus.PAUSED
        pr = PauseRecord(self.session_id, reason)
        self._current_pause = pr
        self.pause_records.append(pr)
        return pr

    def resume(self):
        if self.status != SessionStatus.PAUSED:
            raise RuntimeError("Only PAUSED sessions can be resumed")
        self.status = SessionStatus.ACTIVE
        self._segment_start = time.time()
        if self._current_pause:
            self._current_pause.resumed_at = datetime.now()
            self._current_pause.duration = int(
                (self._current_pause.resumed_at -
                 self._current_pause.paused_at).total_seconds())
            self._current_pause = None

    def end(self, reason: SessionEndReason):
        if reason == SessionEndReason.UPPER_LIMIT:
            self.status = SessionStatus.ENDED_WIN
        elif reason == SessionEndReason.LOWER_LIMIT:
            self.status = SessionStatus.ENDED_LOSS
        elif reason == SessionEndReason.TIMEOUT:
            self.status = SessionStatus.ENDED_TIMEOUT
        else:
            self.status = SessionStatus.ENDED_MANUAL
        self._active_seconds += time.time() - self._segment_start

    def summary(self):
        return {
            "session_id":       self.session_id,
            "status":           self.status.value,
            "initial_stake":    self.params.upper_limit,  # stored in params
            "final_stake":      round(self.current_stake, 2),
            "total_games":      self.total_games,
            "wins":             self.wins,
            "losses":           self.losses,
            "win_rate":         round(self.wins / max(self.total_games, 1) * 100, 1),
            "active_seconds":   round(self.active_duration, 1),
        }
