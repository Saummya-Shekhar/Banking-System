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

router = APIRouter()

@router.post("/")
def create_account(info: CreateAccountRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_account = Account(
        owner_id = user.id,
        account_number = generate_account_number(),
        balance = 0,
        hashed_pin = hash_password(info.pin)
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return {
        "message": "Account Created Successfully",
        "Account Number": new_account.account_number
    }


@router.get("/{account_number}", response_model=AccountSummary)
def get_account_details(account_number: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    account = get_specific_account(user,account_number,db)
    return account

@router.get("/", response_model=list[AccountSummary])
def get_all_accounts(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    accounts = get_all_account(user,db)
    return accounts

@router.post("/{account_number}/deposit")
def deposit(account_number: str, info: DepositRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    account = get_specific_account(user, account_number, db)
    if not verify_password(info.pin, account.hashed_pin):
        slip = create_transaction_slip(db=db,transaction_type=Transaction_Type.DEPOSIT, transaction_status=Transaction_Status.FAILED, sender_id=None, receiver_id=user.id, amount=info.amount)
        db.commit()
        raise HTTPException(
            status_code=401,
            detail="Invalid account number or pin"
        )
    
    
    account.balance += info.amount
    slip = create_transaction_slip(db=db, transaction_type=Transaction_Type.DEPOSIT, transaction_status=Transaction_Status.SUCCESS, sender_id=None, receiver_id=user.id, amount=info.amount)
    db.commit()
    db.refresh(account)
    db.refresh(slip)
    return BasicResponse(
        message=f"Successfully deposited {info.amount} in your account (Account No. {account_number})",
        balance=account.balance,
        slip=slip
    )
    

@router.post("/{account_number}/withdraw")
def withdraw(account_number: str, info: DepositRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    account = get_specific_account(user, account_number, db)
    if not verify_password(info.pin, account.hashed_pin):
        slip = create_transaction_slip(db=db, transaction_type=Transaction_Type.WITHDRAW, transaction_status=Transaction_Status.FAILED, sender_id=user.id, receiver_id=None, amount=info.amount)
        db.commit()
        raise HTTPException(
            status_code=401,
            detail="Invalid account number or pin"
        )
    if info.amount > account.balance:
        slip = create_transaction_slip(db=db, transaction_type=Transaction_Type.WITHDRAW, transaction_status=Transaction_Status.FAILED, sender_id=None, receiver_id=user.id, amount=info.amount)
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="Insufficient Balance"
        )

    account.balance -= info.amount
    slip = create_transaction_slip(db=db, transaction_type=Transaction_Type.WITHDRAW, transaction_status=Transaction_Status.SUCCESS, sender_id=None, receiver_id=user.id, amount=info.amount)
    db.commit()
    db.refresh(account)
    db.refresh(slip)
    return BasicResponse(
        message = f"Successfully withdrew {info.amount} from your account (Account No. {account_number})",
        balance=account.balance,
        slip=slip
    )


@router.post("/{account_number}/transfer")
def transfer(account_number: str, info: TransferRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    sender_account = get_specific_account(user, account_number, db)
    receiver_account = db.query(Account).filter(Account.account_number == info.receiver_account_number).first()

    if not receiver_account:
        raise HTTPException(
            status_code=401,
            detail="Invalid Receiver Account"
        )
    
    if not verify_password(info.pin, sender_account.hashed_pin):
        slip = create_transaction_slip(db=db, transaction_type=Transaction_Type.TRANSFER, transaction_status=Transaction_Status.FAILED, sender_id=user.id, receiver_id=receiver_account.owner_id, amount=info.amount)
        db.commit()
        raise HTTPException(
            status_code=401,
            detail="Invalid Sccount Number or Pin"
        )
    
    if info.amount > sender_account.balance:
        slip = create_transaction_slip(db=db, transaction_type=Transaction_Type.TRANSFER, transaction_status=Transaction_Status.FAILED, sender_id=user.id, receiver_id=receiver_account.owner_id, amount=info.amount)
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="Insufficient Balance"
        )

    sender_account.balance -= info.amount
    receiver_account.balance += info.amount
    db.add(sender_account)
    db.add(receiver_account)
    slip = create_transaction_slip(db=db, transaction_type=Transaction_Type.TRANSFER, transaction_status=Transaction_Status.SUCCESS, sender_id=user.id, receiver_id=receiver_account.owner_id, amount=info.amount)
    db.commit()
    db.refresh(sender_account)
    db.refresh(receiver_account)

    return BasicResponse(
            message = f"Successfully Transferred {info.amount} from {sender_account.account_number} to {receiver_account.account_number}",
            balance=sender_account.balance,
            slip=slip
        )

@router.get("/{account_number}/transactions", response_model=list[TransactionSummary])
def get_all_transactions(account_number:str ,user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    transactions = get_all_transaction(account_number, user, db)
    if not transactions:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return transactions

@router.get("/{account_number}/transactions/{transaction_id}", response_model=TransactionSummary)
def get_specific_transactions(account_number:str ,transaction_id: str ,user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    transaction = get_specific_transaction(account_number,transaction_id, user, db)
    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )
    
    return transaction








