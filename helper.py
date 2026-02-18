import re
import smtplib
import random
import math
from fastapi import HTTPException

def generate_otp():
    digits = "0123456789"
    otp = ""
    for i in range(6):
        otp += digits[math.floor(random.random() * 10)]
    return otp


def send_mail(otp,receiver_mail):
    sender_mail = "test@example.com"
    
    subject = "Your OTP Verification Code"
    body = f"Your OTP is {otp}. It is valid for 5 minutes."
    msg = f"Subject: {subject}\n\n{body}"
    
    try:
        server = smtplib.SMTP('localhost', 1025)
        server.sendmail(sender_mail, receiver_mail, msg)
        server.quit()
        print(f"Postman Test: Mail sent to {receiver_mail}")
    except ConnectionRefusedError:
        print("Error")
    
    
def verify_otp(generated_otp):
    otp=input("enter otp: ")
    if generated_otp==otp:
        print("verified")
        return True
    else:
        print("invalid otp")
        return False


def check_mail(new_email):
    email_pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(email_pattern,new_email):
        return False
    return True