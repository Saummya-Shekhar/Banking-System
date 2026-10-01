from pydantic import BaseModel

class ReadOnlyAgentRquest(BaseModel):
    message: str