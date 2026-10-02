from database import SessionLocal
from models.models import User
from utils.business_logic import get_specific_account
from sqlalchemy.orm import Session
from fastapi import HTTPException
from utils.encrypt import verify_password
from utils.business_logic import create_transaction_slip
from schemas.Enums import Transaction_Type, Transaction_Status
from pydantic import BaseModel

def withdraw_money(account_number: str, amount:int, pin: str,  user: User, db: Session):
    account = get_specific_account(user, account_number, db)
    if not verify_password(pin, account.hashed_pin):
        slip = create_transaction_slip(db=db, transaction_type=Transaction_Type.WITHDRAW, transaction_status=Transaction_Status.FAILED, sender_id=account.id, receiver_id=None, amount=amount)
        db.commit()
        raise HTTPException(
            status_code=401,
            detail="Invalid account number or pin"
        )
    if amount > account.balance:
        slip = create_transaction_slip(db=db, transaction_type=Transaction_Type.WITHDRAW, transaction_status=Transaction_Status.FAILED, sender_id=None, receiver_id=account.id, amount=amount)
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="Insufficient Balance"
        )

    account.balance -= amount
    slip = create_transaction_slip(db=db, transaction_type=Transaction_Type.WITHDRAW, transaction_status=Transaction_Status.SUCCESS, sender_id=None, receiver_id=user.id, amount=amount)
    db.commit()
    db.refresh(account)
    db.refresh(slip)

    return {
            "message": (
                f"Successfully withdrawn {amount} "
                f"from your account (Account No. {account_number})"
            ),
            "balance": account.balance,
            "slip": {
                "transaction_id": slip.transaction_id,
                "type": slip.type.value,
                "status": slip.status.value,
                "amount": slip.amount,
            }
        }

TOOL = {
    "type": "function",
    "name": "withdraw_money",
    "description": "Withdraw money from the specified bank account",
    "parameters": {
        "type": "object",
        "properties": {
            "account_number": {
                "type": "string",
                "description": "The Account Number of the Account from which the money should be withdrawn."
            },
            "amount": {
                "type": "integer",
                "description": "Amount of money to withdraw"
            },
        },
        "required": ["account_number", "amount"],
        "additionalProperties": False
    }
}
    