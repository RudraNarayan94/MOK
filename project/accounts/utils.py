import os
import logging
from django.core.mail import EmailMessage
from smtplib import SMTPAuthenticationError, SMTPException
from .tasks import send_email_task
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
            email.content_subtype = "html"  # Set HTML content
            email.send()
            logger.info(f"Email sent successfully to {data['to_email']}")
        except SMTPAuthenticationError:
            logger.error("SMTP Authentication failed. Check email credentials.")
        except SMTPException as e:
            logger.error(f"SMTP error: {e}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")

    @staticmethod
    def send_welcome_email(user):
        data = {
            "subject": "Welcome to MOK – Ready to Type Like a Speed Demon?",
            "body": f"""
            <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
                <div style="max-width: 600px; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                    <h2 style="color: #007bff;">🚀 Welcome to MOK, {user.username}!</h2>
                    <p>You've officially entered the <strong>Typing Speed Arena</strong>. 🏁</p>
                    <p>Get ready to shatter records, leave typos in the dust, and make your keyboard beg for mercy!</p>
                    <h3 style="color: #28a745;">🔥 Pro Tip:</h3>
                    <p><em>"The spacebar is not just for breathing—it’s for winning!"</em></p>
                    <p>Speed is great, but accuracy? That’s the real flex. 😉</p>
                    <p style="text-align: center;">
                        <a href="http://localhost:3000" style="display: inline-block; padding: 10px 20px; font-size: 16px; color: white; background-color: #007bff; text-decoration: none; border-radius: 5px;">
                            Start Typing Now
                        </a>
                    </p>
                    <p>See you at the leaderboard,</p>
                    <p><strong>The MOK Team</strong> 💻🔥</p>
                </div>
            </body>
            </html>
            """,
            "to_email": user.email,
        }
        try:
            send_email_task.delay(data)
        except Exception as e:
            logger.error("Celery task failed, falling back to synchronous email sending.")
            EmailServices.send_email(data)


    @staticmethod
    def send_password_changed_email(user):
        data = {
                'subject': 'Your Password Has Been Changed Successfully',
                'body': f"""
                <html>
                    <body>
                        <h2 style="color: #333;">Password Changed Successfully</h2>
                        <p>Dear <strong>{user.username}</strong>,</p>
                        <p>Your password has been successfully updated. If you made this change, no further action is needed.</p>
                        <p>If you did <strong>not</strong> request this change, please reset your password immediately and contact our support team.</p>
                        <p>Stay secure,<br><strong>MOK Security Team</strong></p>
                    </body>
                </html>
                """,
                'to_email': user.email,
            }
        try:
            send_email_task.delay(data)
        except Exception as e:
            logger.error("Celery task failed, falling back to synchronous email sending.")
            EmailServices.send_email(data)
        
    @staticmethod
    def send_password_reset_email(user, link):
        data = {
                'subject': 'Reset Your Password',
                'body': f"""
                <html>
                    <body>
                        <h2 style="color: #333;">Password Reset Request</h2>
                        <p>Dear <strong>{user.username}</strong>,</p>
                        <p>You have requested to reset your password. Click the button below to proceed:</p>
                        <p>
                            <a href="{link}" 
                                style="display: inline-block; padding: 10px 20px; font-size: 16px; color: white; background-color: #007BFF; text-decoration: none; border-radius: 5px;">
                                Reset Password
                            </a>
                        </p>
                        <p>If you did not request this, please ignore this email.</p>
                        <p>Stay secure,<br><strong>MOK Security Team</strong></p>
                    </body>
                </html>
                """,
                'to_email': user.email,
            }
        try:
            send_email_task.delay(data)
        except Exception as e:
            logger.error("Celery task failed, falling back to synchronous email sending.")
        EmailServices.send_email(data)
