# backend/app/core/mail.py

import os
import logging
import resend

logger = logging.getLogger(__name__)

# Resend authenticates via an API key, not SMTP credentials.
# This works on all cloud providers including Railway which blocks
# outbound SMTP connections from Google Cloud servers.
resend.api_key = os.environ.get("RESEND_API_KEY")


async def send_otp_email(email: str, otp: str) -> None:
    """
    Sends the OTP login code via Resend's HTTP API.

    Resend is used instead of Gmail SMTP because Railway runs on
    Google Cloud Platform which blocks outbound SMTP to Gmail servers.
    Resend uses HTTPS which is never blocked.

    Args:
        email: the recipient's email address
        otp:   the raw 6-digit OTP code — never the hash
    """
    logger.info(f"Attempting to send OTP email to {email}")

    if not resend.api_key:
        raise ValueError("RESEND_API_KEY environment variable is not set")

    try:
        params: resend.Emails.SendParams = {
            "from": os.environ.get("MAIL_FROM", "StudyBuddy <onboarding@resend.dev>"),
            "to": [email],
            "subject": "Your StudyBuddy login code",
            "html": f"""
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
                  Never share this code with anyone.
                </p>
              </body>
            </html>
            """,
        }

        response = resend.Emails.send(params)
        logger.info(f"OTP email sent successfully. Resend ID: {response['id']}")

    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}")
        logger.error(f"Error: {str(e)}")
        raise