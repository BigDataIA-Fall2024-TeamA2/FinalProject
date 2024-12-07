from pydantic import BaseModel


class QARequest(BaseModel):
    question: str
    model: str
