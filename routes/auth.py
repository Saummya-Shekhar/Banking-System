from fastapi import APIRouter
from schemas.auth import SignupRequest, LoginRequest, ChangePinRequest
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from models.models import User
from fastapi import HTTPException
from utils.encrypt import hash_password
from schemas.Enums import Roles
from utils.encrypt import verify_password
from utils.auth import get_current_user
from utils.auth import create_access_token
from fastapi import Depends
from utils.business_logic import get_specific_account

 
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

@router.post("/{account_number}/change-pin")
def ChangePin(request: ChangePinRequest, account_number: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    account = get_specific_account(user, account_number, db)
    if not account:
        raise HTTPException(
            status_code=401,
            detail="Account not found"
        )

    if not verify_password(request.current_pin, account.hashed_pin):
        raise HTTPException(
            status_code=401,
            detail="Wrong account number or pin"
        )

    account.hashed_pin = hash_password(request.new_pin)
    
    db.commit()
    db.refresh(account)

    return {
        "message": "Pin Changed Successfully!"
    }





    
     



