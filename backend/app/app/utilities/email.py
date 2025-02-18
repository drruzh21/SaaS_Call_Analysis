import asyncio
import logging
from pathlib import Path
from typing import Any, Dict

from jinja2 import Template

from app.core.config import settings
from app.schemas import EmailContent, EmailValidation
from app.utilities.email_sender import default_sender


async def send_email(
    email_to: str,
    subject_template: str = "",
    html_template: str = "",
    environment: Dict[str, Any] = {},
) -> None:
    """Send an email using configured email sender.
    
    Args:
        email_to: Recipient email address
        subject_template: Jinja2 template for email subject
        html_template: Jinja2 template for email HTML content
        environment: Dictionary of variables for template rendering
    
    Raises:
        AssertionError: If email settings are not properly configured
        Exception: If email sending fails
    """
    assert settings.emails_enabled, "no provided configuration for email variables"
    
    # Add server information to environment
    environment["server_host"] = settings.SERVER_HOST
    environment["server_name"] = settings.SERVER_NAME
    environment["server_bot"] = settings.SERVER_BOT
    
    # Render templates
    subject = Template(subject_template).render(**environment)
    html_content = Template(html_template).render(**environment)
    
    # Send email asynchronously using the configured sender
    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(
        None,
        default_sender.send_email,
        email_to,
        subject,
        html_content
    )
    
    if not success:
        raise Exception("Failed to send email")


async def send_email_validation_email(data: EmailValidation) -> None:
    """Send an email validation link to a user.
    
    Args:
        data: EmailValidation object containing email, subject and token
    """
    logging.info(f"Sending email validation to {data.email}")
    subject = f"{settings.PROJECT_NAME} - {data.subject}"
    server_host = settings.SERVER_HOST
    link = f"{server_host}?token={data.token}"
    
    try:
        with open(Path(settings.EMAIL_TEMPLATES_DIR) / "confirm_email.html") as f:
            template_str = f.read()
        await send_email(
            email_to=data.email,
            subject_template=subject,
            html_template=template_str,
            environment={"link": link},
        )
        logging.info(f"Email validation sent successfully to {data.email}")
    except Exception as e:
        logging.error(f"Failed to send validation email to {data.email}: {str(e)}")
        raise


async def send_web_contact_email(data: EmailContent) -> None:
    """Send a contact form email to the system administrator.
    
    Args:
        data: EmailContent object containing subject and content
    """
    logging.info(f"Sending web contact email from {data.email}")
    subject = f"{settings.PROJECT_NAME} - {data.subject}"
    
    try:
        with open(Path(settings.EMAIL_TEMPLATES_DIR) / "web_contact_email.html") as f:
            template_str = f.read()
        await send_email(
            email_to=settings.EMAILS_TO_EMAIL,
            subject_template=subject,
            html_template=template_str,
            environment={"content": data.content, "email": data.email},
        )
        logging.info(f"Web contact email sent successfully from {data.email}")
    except Exception as e:
        logging.error(f"Failed to send web contact email from {data.email}: {str(e)}")
        raise


async def send_test_email(email_to: str) -> None:
    """Send a test email to verify email functionality.
    
    Args:
        email_to: Recipient email address
    """
    logging.info(f"Sending test email to {email_to}")
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    
    try:
        with open(Path(settings.EMAIL_TEMPLATES_DIR) / "test_email.html") as f:
            template_str = f.read()
        await send_email(
            email_to=email_to,
            subject_template=subject,
            html_template=template_str,
            environment={"project_name": settings.PROJECT_NAME, "email": email_to},
        )
        logging.info(f"Test email sent successfully to {email_to}")
    except Exception as e:
        logging.error(f"Failed to send test email to {email_to}: {str(e)}")
        raise


async def send_magic_login_email(email_to: str, token: str) -> None:
    """Send a magic login link email.
    
    Args:
        email_to: Recipient email address
        token: Magic login token
    """
    logging.info(f"Sending magic login email to {email_to}")
    project_name = settings.PROJECT_NAME
    subject = f"Your {project_name} magic login"
    server_host = settings.SERVER_HOST
    link = f"{server_host}?magic={token}"
    
    try:
        with open(Path(settings.EMAIL_TEMPLATES_DIR) / "magic_login.html") as f:
            template_str = f.read()
        await send_email(
            email_to=email_to,
            subject_template=subject,
            html_template=template_str,
            environment={
                "project_name": settings.PROJECT_NAME,
                "valid_minutes": int(settings.ACCESS_TOKEN_EXPIRE_SECONDS / 60),
                "link": link,
            },
        )
        logging.info(f"Magic login email sent successfully to {email_to}")
    except Exception as e:
        logging.error(f"Failed to send magic login email to {email_to}: {str(e)}")
        raise


async def send_reset_password_email(email_to: str, email: str, token: str) -> None:
    """Send a password reset email.
    
    Args:
        email_to: Recipient email address
        email: User's email (might be different from recipient)
        token: Password reset token
    """
    logging.info(f"Sending password reset email to {email_to} for user {email}")
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    server_host = settings.SERVER_HOST
    link = f"{server_host}/reset-password?token={token}"
    
    try:
        with open(Path(settings.EMAIL_TEMPLATES_DIR) / "reset_password.html") as f:
            template_str = f.read()
        await send_email(
            email_to=email_to,
            subject_template=subject,
            html_template=template_str,
            environment={
                "project_name": settings.PROJECT_NAME,
                "username": email,
                "email": email_to,
                "valid_hours": int(settings.ACCESS_TOKEN_EXPIRE_SECONDS / 60),
                "link": link,
            },
        )
        logging.info(f"Password reset email sent successfully to {email_to}")
    except Exception as e:
        logging.error(f"Failed to send password reset email to {email_to}: {str(e)}")
        raise


async def send_new_account_email(email_to: str, username: str, password: str) -> None:
    """Send a new account creation email.
    
    Args:
        email_to: Recipient email address
        username: New user's username
        password: New user's password
    """
    logging.info(f"Sending new account email to {email_to} for user {username}")
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    link = settings.SERVER_HOST
    
    try:
        with open(Path(settings.EMAIL_TEMPLATES_DIR) / "new_account.html") as f:
            template_str = f.read()
        await send_email(
            email_to=email_to,
            subject_template=subject,
            html_template=template_str,
            environment={
                "project_name": settings.PROJECT_NAME,
                "username": username,
                "password": password,
                "email": email_to,
                "link": link,
            },
        )
        logging.info(f"New account email sent successfully to {email_to}")
    except Exception as e:
        logging.error(f"Failed to send new account email to {email_to}: {str(e)}")
        raise
