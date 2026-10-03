from models.models import User, Account
from utils.business_logic import get_specific_account
from sqlalchemy.orm import Session
from fastapi import HTTPException
from utils.encrypt import verify_password
from utils.business_logic import create_transaction_slip
from schemas.Enums import Transaction_Type, Transaction_Status
from pydantic import BaseModel

def transfer_money(account_number: str, receiver_account_number: str, pin: str, amount: int, user: User, db: Session):

    sender_account = get_specific_account(user, account_number, db)
    receiver_account = db.query(Account).filter(Account.account_number == receiver_account_number).first()

    if not receiver_account:
        raise HTTPException(
            status_code=401,
            detail="Invalid Receiver Account"
        )
    
    if not verify_password(pin, sender_account.hashed_pin):
        slip = create_transaction_slip(db=db, transaction_type=Transaction_Type.TRANSFER, transaction_status=Transaction_Status.FAILED, sender_id=sender_account.id, receiver_id=receiver_account.id, amount=amount)
        db.commit()
        raise HTTPException(
            status_code=401,
            detail="Invalid Sccount Number or Pin"
        )
    
    if amount > sender_account.balance:
        slip = create_transaction_slip(db=db, transaction_type=Transaction_Type.TRANSFER, transaction_status=Transaction_Status.FAILED, sender_id=user.id, receiver_id=receiver_account.owner_id, amount=amount)
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="Insufficient Balance"
        )

    sender_account.balance -= amount
    receiver_account.balance += amount
    slip = create_transaction_slip(db=db, transaction_type=Transaction_Type.TRANSFER, transaction_status=Transaction_Status.SUCCESS, sender_id=user.id, receiver_id=receiver_account.owner_id, amount=amount)
    db.commit()
    db.refresh(sender_account)
    db.refresh(receiver_account)

    return {
            "message": (
                f"Successfully transferred {amount} "
                f"from your account (Account No. {account_number}) to {receiver_account_number}"
            ),
            "balance": sender_account.balance,
            "slip": {
                "transaction_id": slip.transaction_id,
                "type": slip.type.value,
                "status": slip.status.value,
                "amount": slip.amount,
            }
        }

TOOL = {
    "type": "function",
    "name": "transfer_money",
    "description": "Transfer money from Sender's bank account to the specified person's bank account.",
    "parameters": {
        "type": "object",
        "properties": {
            "account_number": {
                "type": "string",
                "description": "The Account Number of the Account in which money should be deposited"
            },
            "receiver_account_number": {
                "type": "string",
                "description": "The account number of receiver"
            },
            "amount": {
                "type": "integer",
                "description": "Amount of money to deposit"
            },
        },
        "required": ["account_number","receiver_account_number", "amount"],
        "additionalProperties": False
    }
}