from typing import Optional

from pydantic import BaseModel


class SessionInput(BaseModel):
    title: Optional[str]
