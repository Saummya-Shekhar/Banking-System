from models.models import User
from utils.business_logic import get_specific_account
from sqlalchemy.orm import Session


def get_account_details(account_number: str, db: Session, user: User):
    account = get_specific_account(user, account_number, db)

    return [
        {
            "account_number": account.account_number,
            "balance": account.balance,
        }
    ]

TOOL = {
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
}

