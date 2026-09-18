"""Bounded in-memory conversation sessions for the reviewer demo."""

from collections import OrderedDict
from dataclasses import dataclass, field
from threading import Lock
from uuid import uuid4

from app.models import LandscapeProfile


@dataclass
class Session:
    id: str
    profile: LandscapeProfile = field(default_factory=LandscapeProfile)
    messages: list[dict[str, str]] = field(default_factory=list)


class SessionStore:
    def __init__(self, capacity: int = 200):
        self.capacity = capacity
        self.sessions: OrderedDict[str, Session] = OrderedDict()
        self.lock = Lock()

    def get_or_create(self, session_id: str | None = None) -> Session:
        with self.lock:
            if session_id and session_id in self.sessions:
                session = self.sessions.pop(session_id)
                self.sessions[session_id] = session
                return session
            new_id = session_id or uuid4().hex
            session = Session(id=new_id)
            self.sessions[new_id] = session
            while len(self.sessions) > self.capacity:
                self.sessions.popitem(last=False)
            return session

    def get(self, session_id: str) -> Session | None:
        return self.sessions.get(session_id)

    def merge_profile(self, session: Session, incoming: LandscapeProfile | None) -> None:
        if incoming is None:
            return
        merged = session.profile.model_dump(exclude_none=True)
        merged.update(incoming.model_dump(exclude_none=True))
        session.profile = LandscapeProfile(**merged)

    def delete(self, session_id: str) -> bool:
        with self.lock:
            return self.sessions.pop(session_id, None) is not None
