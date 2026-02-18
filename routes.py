from schemas import ChangeEmail
from helper import check_mail
import bcrypt
import re
from schemas import ChangePassword
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from auth import create_access_token, get_current_user, hash_password, verify_password
from database import get_db
from models import User
from schemas import Token, UserCreate, UserLogin, UserProfile, VerifyEmail
from config import settings
from helper import generate_otp, verify_otp, send_mail


router = APIRouter()


@router.get("/health")
def health_status():
    return {"status": "ok"}


@router.post("/signup", status_code=201)
def signup(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="email already exists")

    otp = int(generate_otp())
    send_mail(otp, user.email)

    hashed_pwd = hash_password(user.password)

    new_user = User(email=user.email, password=hashed_pwd, otp=otp, isverified=False)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "user ban gya"}


@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user.isverified:
        raise HTTPException(status_code=401, detail="email not verified")

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not db_user.is_active:
        raise HTTPException(status_code=400, detail="Account is inactive")

    access_token = create_access_token(data={"sub": db_user.email})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserProfile)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/verify_mail", response_model=dict)
def verify_mail(data: VerifyEmail, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == data.email).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if db_user.otp == data.otp:
        print("yes")
        db_user.isverified = True
        db_user.otp = None
        db.commit()
        return {"message": "Email verified successfully"}

    raise HTTPException(status_code=400, detail="Invalid OTP")


@router.patch("/deactivate")
def deactivate_account(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="pehle se deactivate h")
    current_user.is_active = False
    db.commit()
    return {"message": "kar diya bhai deactivate"}


@router.post("/change-password")
def change_password(
    data:ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if bcrypt.checkpw(data.old_password.encode("utf-8"), current_user.password.encode("utf-8")):
        new_password = hash_password(data.new_password)
        current_user.password = new_password
        db.commit()
        return {"message": "Password badal gya bhai"}

    raise HTTPException(status_code=400, detail="invalid credentials")


@router.put("/change-email")
def change_email(data:ChangeEmail, current_user: User = Depends(get_current_user), db:Session=Depends(get_db)):
    if not current_user or not current_user.is_active:
        raise HTTPException(status_code=400, detail="nhi hoga bhai")

    if not check_mail(data.new_email):
        raise HTTPException(status_code=400, detail="bhai email likhna nhi aata kya")

    existing_email=db.query(User).filter(User.email==data.new_email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="bhai pehle se h, kuchh or try kar")


    current_user.email=data.new_email

    access_token = create_access_token(data={"sub": current_user.email})

    db.commit()
    return {"message":"kar diya bhai email change", "access_token":access_token, "token_type":"bearer"}

    
