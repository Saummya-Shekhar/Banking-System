from enum import Enum 

class Roles(Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class Transaction_Type(Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    TRANSFER = "TRANSFER"

class Transaction_Status(Enum):
    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    FAILED = "FAILED"