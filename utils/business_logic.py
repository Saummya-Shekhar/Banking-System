from database import get_db
from models.models import User, Account
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import Depends
from fastapi import HTTPException
from schemas.accounts import DepositRequest
from models.models import Transaction
from utils.encrypt import generate_transaction_id
from schemas.Enums import Transaction_Type, Transaction_Status

def get_specific_account(user: User,account_number: str, db: Session):
    account = db.query(Account).filter(Account.account_number == account_number, Account.owner_id == user.id).first()
    if not account:
        raise HTTPException(
            status_code=401,
            detail="Account Not Found"
        )

    return account

def get_all_account(user: User, db: Session):
    accounts = db.query(Account).filter(Account.owner_id == user.id).all()
    if not accounts:
        raise HTTPException(
            status_code=401,
            detail="Account Not Found"
        )

    return accounts

def get_all_transaction(account_number: str, user: User, db: Session):
    account = get_specific_account(user, account_number, db)

    transactions = db.query(Transaction).filter(or_(Transaction.sender_account_id == account.id, Transaction.receiver_account_id == account.id)).order_by(Transaction.timestamp.desc()).all()
    return transactions

def get_specific_transaction(account_number: str,transaction_id, user: User, db: Session):
    account = db.query(Account).filter(Account.owner_id == user.id, Account.account_number == account_number).first()
    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account Not Found"
        )

    transaction = db.query(Transaction).filter(and_(or_(Transaction.sender_account_id == account.id, Transaction.receiver_account_id == account.id)),Transaction.transaction_id == transaction_id).first()
    return transaction



def create_transaction_slip(
    db: Session,
    amount: float,
    transaction_type: Transaction_Type,
    transaction_status: Transaction_Status,
    sender_id: int | None = None,
    receiver_id: int | None = None,
):
    slip = Transaction(
        transaction_id=generate_transaction_id(),
        type=transaction_type,
        status=transaction_status,
        sender_account_id=sender_id,
        receiver_account_id=receiver_id,
        amount=amount,
    )

    db.add(slip)
    return slip















