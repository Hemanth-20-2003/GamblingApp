"""Pause record data class for UC4 Game Session Management"""
from datetime import datetime


class PauseRecord:
    def __init__(self, session_id, reason=""):
        self.session_id = session_id
        self.reason     = reason
        self.paused_at  = datetime.now()
        self.resumed_at = None
        self.duration   = None
        self.id         = None
from datetime import datetime


class PauseRecord:
    def __init__(self, session_id, reason=""):
        self.session_id = session_id
        self.reason     = reason
        self.paused_at  = datetime.now()
        self.resumed_at = None
        self.duration   = None
        self.id         = None
