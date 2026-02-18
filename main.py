from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from auth import create_access_token, get_current_user, hash_password, verify_password
from database import get_db
from models import User
from schemas import Token, UserCreate, UserLogin, UserProfile, VerifyEmail
from config import settings
from helper import generate_otp, verify_otp, send_mail


app = FastAPI()


@app.post("/signup", status_code=201)
def signup(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="email already exists")

    otp = int(generate_otp())
    send_mail(otp, user.email)

    hashed_pwd = hash_password(user.password)

    new_user = User(
        email=user.email, password=hashed_pwd, otp=otp, isverified=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "user ban gya"}


@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == user.email).first()

    if db_user.isverified == False:
        raise HTTPException(status_code=401, detail="email not verified")

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": db_user.email})

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=UserProfile)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/verify_mail", response_model=dict)
def verify_mail(data: VerifyEmail, db:Session=Depends(get_db)):
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