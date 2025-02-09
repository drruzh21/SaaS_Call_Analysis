"""Email sender interface and implementation for Mail.ru SMTP.

This module provides a clean interface for sending emails and its Mail.ru implementation.
Following SOLID principles, particularly Interface Segregation and Dependency Inversion.
"""

from abc import ABC, abstractmethod
import logging
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from typing import Protocol

from app.core.config import settings


class EmailSender(Protocol):
    """Protocol defining the interface for sending emails."""
    
    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send an email with HTML content.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        ...


class MailRuSender:
    """Mail.ru SMTP implementation of the EmailSender protocol."""
    
    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send an email using Mail.ru SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(html_content, 'html'))
            
            # Create SSL context with secure defaults
            context = ssl.create_default_context()
            
            # Connect using SSL context
            with smtplib.SMTP_SSL(
                settings.SMTP_HOST,
                port=465,  # Mail.ru requires SSL on port 465
                context=context,
                timeout=10  # Add timeout to prevent hanging
            ) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
                
            logging.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send email to {to_email}: {str(e)}")
            return False


# Default sender instance using Mail.ru
default_sender = MailRuSender()
