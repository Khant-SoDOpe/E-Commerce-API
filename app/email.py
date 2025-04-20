import logging  # Import logging module
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
import os
from dotenv import load_dotenv
from typing import List
from fastapi import HTTPException

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", "resend"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.resend.com"),
    MAIL_STARTTLS=True if os.getenv("MAIL_STARTTLS", "true").lower() == "true" else False,
    MAIL_SSL_TLS=False if os.getenv("MAIL_STARTTLS", "true").lower() == "true" else True,  # Ensure mutual exclusivity
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True  # Ensure certificates are validated
)

if not conf.MAIL_USERNAME or not conf.MAIL_PASSWORD:
    raise ValueError("Email configuration is incomplete. Check MAIL_USERNAME and MAIL_PASSWORD.")

async def send_email_with_retry(message: MessageSchema, retries: int = 3):
    """Retry email sending to handle transient errors."""
    fm = FastMail(conf)
    for attempt in range(retries):
        try:
            await fm.send_message(message)
            return
        except Exception as e:
            if attempt < retries - 1:
                logger.warning(f"Retrying email send: {str(e)}")
            else:
                logger.error(f"Failed to send email after {retries} attempts: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to send email")

async def send_verification_email(email: EmailStr, token: str):
    """Send a verification email."""
    api_url = os.getenv("API_URL", "http://localhost:8000")
    verification_url = f"{api_url}/auth/verify?token={token}"
    
    html_content = f"""
    <h3>Welcome to Our Platform!</h3>
    <p>Please verify your email by clicking the link below:</p>
    <p><a href="{verification_url}">Verify Email</a></p>
    <p>If you didn't request this verification, please ignore this email.</p>
    """

    message = MessageSchema(
        subject="Verify your email",
        recipients=[email],
        body=html_content,
        subtype="html"
    )

    try:
        await send_email_with_retry(message)
        logger.info(f"Verification email sent successfully to {email}")
    except Exception as e:
        logger.error(f"Error sending verification email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")

async def send_password_reset_email(email: EmailStr, token: str):
    """Send a password reset email."""
    api_url = os.getenv("API_URL", "http://localhost:8000")
    reset_url = f"{api_url}/auth/reset-password?token={token}"
    
    html_content = f"""
    <h3>Password Reset Request</h3>
    <p>You have requested to reset your password. Click the link below to reset it:</p>
    <p><a href="{reset_url}">Reset Password</a></p>
    <p>If you didn't request this reset, please ignore this email.</p>
    <p>This link will expire in 1 hour.</p>
    """

    message = MessageSchema(
        subject="Reset Your Password",
        recipients=[email],
        body=html_content,
        subtype="html"
    )

    try:
        await send_email_with_retry(message)
        logger.info(f"Password reset email sent successfully to {email}")
    except Exception as e:
        logger.error(f"Error sending password reset email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error sending password reset email: {str(e)}")
