from fastapi import APIRouter
from schemas.auth import CreateAccountRequest
from schemas.accounts import AccountSummary, DepositRequest, TransferRequest, BasicResponse, TransactionSummary
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from models.models import User
from fastapi import HTTPException
from schemas.Enums import Transaction_Status, Transaction_Type
from utils.encrypt import verify_password
from utils.auth import get_current_user
from models.models import Account
from utils.business_logic import get_specific_account, get_all_account, get_all_transaction, get_specific_transaction
from utils.encrypt import hash_password, generate_account_number
from utils.business_logic import create_transaction_slip
from schemas.agent import ReadOnlyAgentRquest, ReadAndWriteAgentRequest
from agent.agent import run_agent

router = APIRouter()

@router.get("/")
def agent(prompt: ReadOnlyAgentRquest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return run_agent(prompt.message, db, user)

@router.post("/")
def agent(prompt: ReadAndWriteAgentRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return run_agent(prompt.message, db, user, prompt.pin)





