from celery import shared_task
from django.core.mail import EmailMessage
import os

@shared_task
def send_email_task(data):
        email = EmailMessage(
            subject=data["subject"],
            body=data["body"],
            from_email=os.environ.get("EMAIL_FROM"),
            to=[data["to_email"]],
        )
        email.content_subtype = "html"  # Set HTML content
        email.send()
            

