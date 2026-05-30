from pydantic import BaseModel


class Message(BaseModel):
    status: str = "success"
    message: str
