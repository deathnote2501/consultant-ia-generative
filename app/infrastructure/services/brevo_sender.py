import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from app.core.ports.email_sender import EmailSenderInterface
from app.core.config import settings
import logging

# Configure logging
logger = logging.getLogger(__name__)

class BrevoEmailSender(EmailSenderInterface):
    """
    Implementation of EmailSenderInterface using Brevo (Sendinblue) API.
    """

    def __init__(self):
        self.api_key = settings.BREVO_API_KEY
        self.default_sender_email = settings.BREVO_SENDER_EMAIL
        self.default_sender_name = settings.BREVO_SENDER_NAME

        if not self.api_key or self.api_key == "your_brevo_api_key_here": # Also check for placeholder
            logger.error("Brevo API key is not configured or is using placeholder.")
            raise ValueError("Brevo API key must be set in settings and not be the placeholder.")
        if not self.default_sender_email or self.default_sender_email == "sender@example.com": # Also check for placeholder
            logger.error("Brevo default sender email is not configured or is using placeholder.")
            raise ValueError("Brevo default sender email must be set in settings and not be the placeholder.")

        self.configuration = sib_api_v3_sdk.Configuration()
        self.configuration.api_key['api-key'] = self.api_key
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(self.configuration)
        )

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        sender_name: str = None,
        sender_email: str = None
    ) -> bool:
        """
        Sends an email using Brevo API.
        """
        current_sender_email = sender_email or self.default_sender_email
        current_sender_name = sender_name or self.default_sender_name

        if not current_sender_email: # Should be caught by __init__ if defaults are also missing
            logger.error("Sender email is not specified and no default is configured.")
            return False

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[sib_api_v3_sdk.SendSmtpEmailTo(email=to_email)],
            sender=sib_api_v3_sdk.SendSmtpEmailSender(email=current_sender_email, name=current_sender_name),
            subject=subject,
            html_content=html_content
        )

        try:
            logger.info(f"Attempting to send email to {to_email} with subject '{subject}' via Brevo.")
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Email sent successfully to {to_email}. Brevo API Response: {api_response.message_id}") # Log message_id
            return True
        except ApiException as e:
            logger.error(f"Failed to send email to {to_email} via Brevo. Status: {e.status}, Reason: {e.reason}, Body: {e.body}")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred while sending email to {to_email} via Brevo: {e}")
            return False
