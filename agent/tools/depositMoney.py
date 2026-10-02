from models.models import User
from utils.business_logic import get_specific_account
from sqlalchemy.orm import Session
from fastapi import HTTPException
from utils.encrypt import verify_password
from utils.business_logic import create_transaction_slip
from schemas.Enums import Transaction_Type, Transaction_Status
from pydantic import BaseModel

def deposit_money(account_number: str, amount: float, pin: str, db: Session, user: User):
    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Deposit amount must be greater than 0"
        )

    account = get_specific_account(user=user,account_number=account_number,db=db)

    if not verify_password(pin, account.hashed_pin):
        slip = create_transaction_slip(db=db, transaction_type=Transaction_Type.DEPOSIT, transaction_status=Transaction_Status.FAILED, sender_id=None, receiver_id=account.id, amount=amount)

        db.commit()

        raise HTTPException(
            status_code=401,
            detail="Invalid account number or pin"
        )

    account.balance += amount

    slip = create_transaction_slip(db=db, transaction_type=Transaction_Type.DEPOSIT, transaction_status=Transaction_Status.SUCCESS, sender_id=None, receiver_id=account.id, amount=amount)

    db.commit()

    return {
        "message": (
            f"Successfully deposited {amount} "
            f"in your account (Account No. {account_number})"
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
    "name": "desposit_money",
    "description": "Deposit money into the specified bank account",
    "parameters": {
        "type": "object",
        "properties": {
            "account_number": {
                "type": "string",
                "description": "The Account Number of the Account in which money should be deposited"
            },
            "amount": {
                "type": "integer",
                "description": "Amount of money to deposit"
            },
        },
        "required": ["account_number", "amount"],
        "additionalProperties": False
    }
}