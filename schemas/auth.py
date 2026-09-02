from pydantic import BaseModel, Field
from typing import Annotated
from pydantic import EmailStr
from datetime import date

Pin = Annotated[
    str,
    Field(pattern=r"^\d{4}$")
]

class SignupRequest(BaseModel):
    username: str 
    email: EmailStr
    dob: date
    password: str  

class LoginRequest(BaseModel):
    username: str 
    password: str 

class LoginResponse(BaseModel):
    access_token: str
    token_type: str

class CreateAccountRequest(BaseModel):
    pin: Pin

class ChangePinRequest(BaseModel):
    current_pin: Pin
    new_pin: Pin

