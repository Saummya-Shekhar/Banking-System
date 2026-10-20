from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import date
from Enums import Roles


class UserProfileResponse(BaseModel):
    name: str
    email: EmailStr
    dob: date 
    role: Roles
    model_config = ConfigDict(from_attributes=True)




