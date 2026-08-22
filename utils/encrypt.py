from pwdlib import PasswordHash
import uuid
import secrets

password_hasher = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hasher.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return password_hasher.verify(password, hashed_password)

def generate_transaction_id() -> str:
    return str(uuid.uuid4())

def generate_account_number() -> str:
    prefix = "ACC"
    suffix = str(secrets.randbelow(9000000) + 1000000)
    return prefix + suffix

