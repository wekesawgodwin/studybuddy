# backend/app/core/mail.py

import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

# Gmail SMTP configuration.
#
# Important facts about these values:
#
# MAIL_USERNAME  — your full Gmail address e.g. yourname@gmail.com
# MAIL_PASSWORD  — NOT your Gmail login password. This must be a Gmail App
#                  Password generated at myaccount.google.com/apppasswords.
#                  It is a 16-character string with the spaces removed.
#                  Example: abcdefghijklmnop
#
# MAIL_FROM      — must also be your Gmail address. Gmail's SMTP server
#                  rejects emails where the From address does not match
#                  the authenticated account.
#
# MAIL_SERVER    — always smtp.gmail.com for Gmail
#
# MAIL_PORT      — 587 for Gmail. Gmail supports two port options:
#                  587 with STARTTLS (what we use here) or
#                  465 with SSL_TLS. Port 587 + STARTTLS is the modern
#                  standard and works reliably across all environments.
#
# MAIL_STARTTLS  — True when using port 587
# MAIL_SSL_TLS   — False when using port 587 (mutually exclusive with STARTTLS)

mail_config = ConnectionConfig(
    MAIL_USERNAME=os.environ.get("MAIL_USERNAME"),
    MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD"),
    MAIL_FROM=os.environ.get("MAIL_FROM"),
    MAIL_PORT=int(os.environ.get("MAIL_PORT", 587)),
    MAIL_SERVER=os.environ.get("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_FROM_NAME=os.environ.get("MAIL_FROM_NAME", "StudyBuddy"),

    # Port 587 requires STARTTLS=True and SSL_TLS=False.
    # These two settings are mutually exclusive — enabling both will cause
    # a connection error.
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,

    # USE_CREDENTIALS must be True when a username and password are provided.
    USE_CREDENTIALS=True,

    # VALIDATE_CERTS=True verifies Gmail's SSL certificate during the
    # STARTTLS handshake. Always keep this True in production.
    # Setting it to False would expose the connection to MITM attacks.
    VALIDATE_CERTS=True,
)

# Initialise FastMail once at module load.
# This instance is reused for every email send — creating a new instance
# per request would open a new SMTP connection each time, which is slow.
fastmail = FastMail(mail_config)


async def send_otp_email(email: str, otp: str) -> None:
    """
    Sends the OTP login code to the user's email address via Gmail SMTP.

    This function is async because fastapi-mail uses async I/O.
    It is called via FastAPI's BackgroundTasks so the HTTP response
    returns immediately while the email sends in the background.

    Args:
        email: the recipient's email address
        otp:   the raw 6-digit OTP code — never the hash
    """
    message = MessageSchema(
        subject="Your StudyBuddy login code",
        recipients=[email],
        body=f"""
        <html>
          <body style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto;">

            <h2 style="color: #1a1a1a;">Your StudyBuddy Login Code</h2>

            <p style="color: #444;">
              Use the code below to sign in to StudyBuddy.
              It expires in <strong>10 minutes</strong>.
            </p>

            <div style="
              font-size: 40px;
              font-weight: bold;
              letter-spacing: 12px;
              text-align: center;
              padding: 24px;
              background: #f4f4f4;
              border-radius: 8px;
              margin: 24px 0;
              color: #1a1a1a;
            ">
              {otp}
            </div>

            <p style="color: #888; font-size: 13px;">
              If you did not request this code, you can safely ignore this email.
              Never share this code with anyone — StudyBuddy staff will never ask for it.
            </p>

            <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;" />

            <p style="color: #aaa; font-size: 12px;">
              Sent from StudyBuddy via Gmail SMTP
            </p>

          </body>
        </html>
        """,
        subtype=MessageType.html
    )

    await fastmail.send_message(message)