from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    otp: str|None=None
    isverified: bool=False
    is_active: bool=True
    reset_token: str|None=None
    reset_token_expiry: datetime|None=None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserProfile(BaseModel):
    id: int
    email: str
    isverified: bool
    is_active: bool
    reset_token: str|None=None
    reset_token_expiry: datetime|None=None
    

class VerifyEmail(BaseModel):
    email: str
    otp: int


class ChangePassword(BaseModel):
    old_password: str
    new_password: str


class ChangeEmail(BaseModel):
    new_email: EmailStr


class ResetPassword(BaseModel):
    new_password: str