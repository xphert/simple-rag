from pydantic import BaseModel
class AskRequest(BaseModel):
    question: str
class BriefRequest(BaseModel):
    topic: str