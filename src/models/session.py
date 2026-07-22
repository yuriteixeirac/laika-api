from datetime import datetime
from typing import Optional


class Session:
    def __init__(self, id: Optional[int] = None, title: Optional[str] = None, created_at: Optional[datetime] = None) -> None:
        self.id = id
        self._title = title
        self._created_at = datetime.utcnow()

    @property
    def title(self) -> str:
        return self._title or f"{self.id} at {self.created_at}"

    @property
    def created_at(self) -> str:
        return self._created_at.isoformat()

    def __str__(self) -> str:
        return f"{self.id} - {self.title}"
