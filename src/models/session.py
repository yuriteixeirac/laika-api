from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel


class Session(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = ""
    created_at: datetime = datetime.now(timezone.utc)
