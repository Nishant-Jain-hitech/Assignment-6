import re
import math
import random
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import settings

def generate_otp():
    digits = "0123456789"
    otp = ""
    for i in range(6):
        otp += digits[math.floor(random.random() * 10)]
    return otp


def send_mail(otp:int, to_email:str):
    subject = "Your OTP Verification Code"
    body = f"""
    Hello,
 
    Your OTP code is: {otp}
 
    Please use this to verify your account.
 
    Thank you!
    """
 
    msg = MIMEMultipart()
    msg["From"] = settings.EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject
 
    msg.attach(MIMEText(body, "plain"))
 
    server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
    server.starttls()
    server.login(settings.EMAIL_ADDRESS, settings.EMAIL_PASSWORD)
    server.sendmail(settings.EMAIL_ADDRESS, to_email, msg.as_string())
    server.quit()
    
    
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
