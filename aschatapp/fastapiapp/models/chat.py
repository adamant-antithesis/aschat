from pydantic import BaseModel
from typing import List
from datetime import datetime


class ChatMessage(BaseModel):
    user_id: int
    message: str
    timestamp: datetime


class ChatHistory(BaseModel):
    chat_id: str
    messages: List[ChatMessage]
