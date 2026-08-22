from enum import Enum 
from pydantic import BaseModel, Field
from typing import Annotated
from pydantic import EmailStr
from datetime import datetime
from schemas.Enums import Transaction_Status, Transaction_Type
from pydantic import ConfigDict


Pin = Annotated[
    str,
    Field(pattern=r"^\d{4}$")
]

class AccountSummary(BaseModel):
    account_number: str
    balance: float 
    model_config = ConfigDict(from_attributes=True)

class CreateAccountRequest(BaseModel):
    pin: Pin

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

class DepositRequest(BaseModel):
    amount: float = Field(gt=0)
    pin: Pin

class WithdrawRequest(BaseModel):
    amount: float = Field(gt=0)
    pin: Pin

class TransferRequest(BaseModel):
    receiver_account_number: str
    amount: float = Field(gt=0)
    pin: Pin

class TransactionSummary(BaseModel):
    transaction_id: str
    amount: float
    type: Transaction_Type
    status: Transaction_Status
    timestamp: datetime
    receiver_account_number: str | None = None
    sender_account_number: str | None = None
    model_config = ConfigDict(from_attributes=True)



class BasicResponse(BaseModel):
    message: str 
    balance: float 
    slip: TransactionSummary
    model_config = ConfigDict(from_attributes=True)
