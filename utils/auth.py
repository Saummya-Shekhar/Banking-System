import jwt 
from jwt.exceptions import InvalidTokenError
from database import get_db
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from schemas.auth import LoginRequest
from datetime import datetime, timezone, timedelta
from models.models import User
from config import SECRET_KEY
from fastapi import HTTPException
from sqlalchemy.orm import Session
from schemas.Enums import Roles

ALGORITHM = "HS256"
oAuth2Scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_access_token(user: User)->str:
    expiration = datetime.now(timezone.utc) + timedelta(minutes=30)

    payload = {
        "sub": str(user.id),
        "role": user.role.value,
        "exp": expiration
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY,algorithms=[ALGORITHM])
        return payload
    except InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )

def get_current_user(token: str = Depends(oAuth2Scheme), db: Session = Depends(get_db))->User:
    payload = decode_access_token(token)
    user_id = int(payload.get("sub"))
    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="User Not Found"
        )

    existing_user = db.query(User).filter(User.id == user_id).first()

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="User Not Found"
        )

    return existing_user

def require_role(role: Roles):
    def checker(user: User = Depends(get_current_user)):
        if user.role == role:
            return user
        else:
            raise HTTPException(
                status_code=403,
                detail=f"Only {role.value}s can access this endpoint"
            )
        
    return checker



