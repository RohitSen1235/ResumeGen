import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Optional
from fastapi import HTTPException

def send_email(
    to_email: str,
    subject: str,
    message: str,
    html_content: Optional[str] = None
) -> bool:
    """Send email using SMTP configuration from environment variables."""
    
    # Get SMTP configuration from environment
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    from_email = os.getenv('SMTP_FROM_EMAIL', smtp_user)

    if not all([smtp_host, smtp_user, smtp_password]):
        raise HTTPException(
            status_code=500,
            detail="SMTP configuration is incomplete"
        )

    try:
        # Create message container
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email

        # Record the MIME types of both parts - text/plain and text/html
        part1 = MIMEText(message, 'plain')
        msg.attach(part1)

        if html_content:
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)

        # Send the message via SMTP server
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(from_email, to_email, msg.as_string())
        
        return True

    except smtplib.SMTPException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send email: {str(e)}"
        )
