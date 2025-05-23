#when matching jobs are found -> sends a notification
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os
from utils.logger import logger

#load environment variables from .env file
load_dotenv() #not hard coding sensitive info

def send_email(subject, body):
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = os.getenv('EMAIL_USER')
        msg['To'] = os.getenv('EMAIL_TO')

        with smtplib.SMTP(os.getenv('EMAIL_HOST'), int(os.getenv('EMAIL_PORT'))) as server:
            server.starttls() #secures the connection
            server.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASS')) #login with given credentials
            server.send_message(msg)

        logger.info("Email sent successfully.")

    except Exception as e:
        logger.error(f"Failed to send email: {e}")