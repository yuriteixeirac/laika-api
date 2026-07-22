from pydantic import BaseModel


class SessionInput(BaseModel):
    title: str


class LLMInput(BaseModel):
    prompt: str
