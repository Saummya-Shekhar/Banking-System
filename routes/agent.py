from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from models.models import User
from utils.auth import get_current_user
from utils.agent import get_or_create_conversation
from schemas.agent import ReadOnlyAgentRquest, ReadAndWriteAgentRequest
from agent.agent import run_agent

router = APIRouter()

@router.get("/")
def agent(prompt: ReadOnlyAgentRquest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = get_or_create_conversation(user,db)
    return run_agent(prompt.message, db, user, conversation_id=conversation.id)

@router.post("/")
def agent(prompt: ReadAndWriteAgentRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = get_or_create_conversation(user,db)
    return run_agent(prompt.message, db, user, prompt.pin, conversation_id=conversation.id)





