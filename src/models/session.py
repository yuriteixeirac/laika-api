from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Session:
    id: int
    title: Optional[str]
    created_at: datetime
