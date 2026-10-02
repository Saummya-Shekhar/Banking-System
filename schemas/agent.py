from pydantic import BaseModel
from schemas.accounts import Pin

class ReadOnlyAgentRquest(BaseModel):
    message: str

class ReadAndWriteAgentRequest(BaseModel):
    message: str
    pin: Pin


