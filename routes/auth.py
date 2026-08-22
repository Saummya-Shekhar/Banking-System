from fastapi import APIRouter
from schemas.auth import SignupRequest, LoginRequest
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from models.models import User
from fastapi import HTTPException
from utils.encrypt import hash_password
from schemas.Enums import Roles
from utils.encrypt import verify_password
from utils.auth import get_current_user
from utils.auth import create_access_token, decode_access_token
from models.models import Account
from utils.encrypt import generate_account_number

 
router = APIRouter()

@router.post("/signup")
def signup(signup: SignupRequest, db: Session = Depends(get_db)):
    existing_username = db.query(User).filter(User.username == signup.username).first()
    if existing_username:
        raise HTTPException(
            status_code=409,
            detail = "User Already Exists"
        )

    existing_email = db.query(User).filter(User.email == signup.email).first()
    if existing_email:
            raise HTTPException(
                status_code=409,
                detail = "User Already Exists"
            )
    
    new_user = User(
        username = signup.username,
        email = signup.email,
        dob = signup.dob,
        hashed_password = hash_password(signup.password),
        role = Roles.USER
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User Created Successfully! Login to create/access accounts"
    }

@router.post("/login")
def Login(login: LoginRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == login.username).first()
    if not existing_user:
         raise HTTPException(
              status_code=408,
              detail="Invalid Username or Password"
         )

    if not verify_password(login.password, existing_user.hashed_password):
         raise HTTPException(
              status_code=401,
              detail = "Invalid Username or Password"
        )

    token = create_access_token(existing_user)

    return {
         "access_token": token,
         "token_type": "Bearer"
    }



