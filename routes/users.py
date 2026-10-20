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
from schemas.users import UserProfileResponse

router = APIRouter()

@router.get("/me", response_model=UserProfileResponse)
def show_user_profile(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return user


    