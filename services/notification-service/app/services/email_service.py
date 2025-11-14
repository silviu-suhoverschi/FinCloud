"""
Email notification service using SMTP
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
import structlog

from app.core.config import settings
from app.schemas.notification import EmailNotification

logger = structlog.get_logger()


class EmailService:
    """Email notification service"""

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
        self.from_name = settings.SMTP_FROM_NAME
        self.use_tls = settings.SMTP_USE_TLS

    def is_configured(self) -> bool:
        """Check if email service is properly configured"""
        return all([
            self.smtp_host,
            self.smtp_user,
            self.smtp_password,
        ])

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> bool:
        """
        Send an email

        Args:
            to: Recipient email address
            subject: Email subject
            body: Plain text body
            html: HTML body (optional)
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)

        Returns:
            True if email was sent successfully
        """
        if not self.is_configured():
            logger.warning("email_service_not_configured")
            return False

        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to

            if cc:
                message["Cc"] = ", ".join(cc)
            if bcc:
                message["Bcc"] = ", ".join(bcc)

            # Add plain text part
            text_part = MIMEText(body, "plain")
            message.attach(text_part)

            # Add HTML part if provided
            if html:
                html_part = MIMEText(html, "html")
                message.attach(html_part)

            # Send email
            async with aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=self.use_tls,
            ) as smtp:
                await smtp.login(self.smtp_user, self.smtp_password)
                await smtp.send_message(message)

            logger.info(
                "email_sent",
                to=to,
                subject=subject,
            )
            return True

        except Exception as e:
            logger.error(
                "email_send_failed",
                to=to,
                subject=subject,
                error=str(e),
            )
            return False

    async def send_notification(self, notification: EmailNotification) -> bool:
        """
        Send email notification

        Args:
            notification: Email notification data

        Returns:
            True if email was sent successfully
        """
        return await self.send_email(
            to=notification.to,
            subject=notification.subject,
            body=notification.body,
            html=notification.html,
            cc=notification.cc,
            bcc=notification.bcc,
        )
