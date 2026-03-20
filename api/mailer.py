import smtplib
import imaplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import time
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.hostinger.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
IMAP_HOST = os.getenv("IMAP_HOST", "imap.hostinger.com")
IMAP_PORT = int(os.getenv("IMAP_PORT", 993))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

# Replace this with your actual Vercel domain once deployed
PUBLIC_URL = "https://your-vercel-domain.vercel.app"

def send_email(to_address, subject, body_content):
    msg = MIMEMultipart('alternative')
    msg['From'] = SMTP_USER
    msg['To'] = to_address
    msg['Subject'] = subject

    # Convert plain text newlines to HTML breaks for proper formatting
    html_body_content = body_content.replace('\n', '<br>')

    # HTML Signature Template using Flowmotive branding
    html_content = f"""
    <html>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; color: #333333; line-height: 1.6;">
        <p>{html_body_content}</p>
        <br><br>
        <table style="border-top: 2px solid #2A004D; padding-top: 15px; width: 100%; max-width: 450px;">
            <tr>
                <td style="width: 80px; vertical-align: middle;">
                    <img src="{PUBLIC_URL}/flowmotive.png" alt="Flowmotive Logo" style="width: 70px; height: auto; display: block;">
                </td>
                <td style="vertical-align: middle; padding-left: 15px;">
                    <h3 style="margin: 0; color: #2A004D; font-size: 16px;">Flowmotive</h3>
                    <p style="margin: 2px 0 8px 0; color: #4A4A4A; font-size: 12px; font-weight: bold;">ADVANCED AI & ML SOLUTIONS</p>
                    <div>
                        <a href="[YOUR_FACEBOOK_LINK]" style="color: #2A004D; text-decoration: none; font-size: 12px; margin-right: 12px; font-weight: bold;">Facebook</a>
                        <a href="[YOUR_INSTAGRAM_LINK]" style="color: #2A004D; text-decoration: none; font-size: 12px; margin-right: 12px; font-weight: bold;">Instagram</a>
                        <a href="[YOUR_YOUTUBE_LINK]" style="color: #2A004D; text-decoration: none; font-size: 12px; font-weight: bold;">YouTube</a>
                    </div>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    msg.attach(MIMEText(body_content, 'plain'))
    msg.attach(MIMEText(html_content, 'html'))

    try:
        # 1. Send via SMTP
        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        
        # 2. Append to Sent folder via IMAP
        try:
            imap = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
            imap.login(SMTP_USER, SMTP_PASS)
            # Hostinger typically uses 'Sent' for the sent mailbox
            imap.append('Sent', '\\Seen', imaplib.Time2Internaldate(time.time()), msg.as_bytes())
            imap.logout()
        except Exception as imap_err:
            print(f"IMAP Append Error: {imap_err}")
            pass

        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False
