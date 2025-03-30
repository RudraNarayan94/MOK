import os
import logging
from smtplib import SMTPAuthenticationError, SMTPException
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)

class EmailServices:
    @staticmethod
    def send_email(data):
        try:
            email = EmailMessage(
                subject=data["subject"],
                body=data["body"],
                from_email=os.environ.get("EMAIL_FROM"),
                to=[data["to_email"]],
            )
            email.content_subtype = "html"
            email.send()
            logger.info(f"Email sent successfully to {data['to_email']}")
        
        except SMTPAuthenticationError:
            logger.error("SMTP Authentication failed. Check email credentials.")
        
        except SMTPException as e:
            logger.error(f"SMTP error occurred: {e}")
        
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
