from database import SessionLocal
from models.models import User, Transaction, Account
from utils.business_logic import get_specific_account, get_all_transaction
from sqlalchemy.orm import Session
from sqlalchemy import or_

def get_account_details(account_number: str, db: Session, user: User):
    account = get_specific_account(user, account_number, db)

    return [
        {
            "account_id": account.id,
            "account_number": account.account_number,
            "balance": account.balance,
        }
    ]

def get_transaction_history(account_number: str, db: Session, user: User):
    try: 
        account = get_specific_account(user,account_number,db)
        transactions = get_all_transaction(account_number,user,db)
        return {
            "current_account_balance": account.balance,
            "transactions": [
                {
                    "transaction_id": transaction.transaction_id,
                    "type": transaction.type.value,
                    "status": transaction.status.value,
                    "amount": transaction.amount,
                    "receiver_account_number": (
                        transaction.receiver_account.account_number
                        if transaction.receiver_account
                        else None
                    ),
                    "sender_account_number": (
                        transaction.sender_account.account_number
                        if transaction.sender_account
                        else None
                        ),
                    }
                for transaction in transactions
                ],
            }
        
    finally:
        db.close()



    



TOOL_MAP = {
    "get_account": get_account_details,
    "get_transaction_history": get_transaction_history
}



Tools = [
{
    "type": "function",
    "name": "get_account_details",
    "description": "Get all bank accounts belonging to a specific user, including account ID, account number, and current balance.",
    "parameters": {
        "type": "object",
        "properties": {
            "account_number": {
                "type": "string",
                "description": "The account number of the account whose details should be retrieved.",
            }
        },
        "required": ["account_number"],
        "additionalProperties": False
    }
}, {
    "type": "function",
    "name": "get_transaction_history",
    "description": "Get all bank accounts history and transaction slips belonging to a specific account, including transaction ID, account number, amount, transaction status",
    "parameters": {
        "type": "object",
        "properties": {
            "account_number": {
                "type": "string",
                "description": "The Account Number of the Account whose Transaction history should be retrieved.",
            }
        },
        "required": ["account_number"],
        "additionalProperties": False
    }
},
]


