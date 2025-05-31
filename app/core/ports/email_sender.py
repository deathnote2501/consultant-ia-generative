from abc import ABC, abstractmethod

class EmailSenderInterface(ABC):
    """
    Interface for an email sending service.
    """

    @abstractmethod
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        sender_name: str = None, # Optional sender name
        sender_email: str = None # Optional sender email (might be fixed by implementation)
    ) -> bool:
        """
        Sends an email.

        Args:
            to_email: The recipient's email address.
            subject: The subject of the email.
            html_content: The HTML content of the email.
            sender_name: Optional name of the sender.
            sender_email: Optional email of the sender.

        Returns:
            True if the email was sent successfully, False otherwise.
        """
        pass
