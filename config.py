# Email configuration
EMAIL = "your_email@example.com"
PASSWORD = "your_email_password"
IMAP_SERVER = "imap.example.com"
IMAP_PORT = 993

# Telegram configuration
TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"
TELEGRAM_CHAT_ID = "your_telegram_chat_id"
MESSAGE_PARSE_MODE = "HTML"

# Script configuration
RETRY_TIME = 60  # Time for checking emails
MESSAGE_TEMPLATE = """
✉️*New mail has been received at {date}*✉️
Sender: {sender_name} ({sender_address})

*{subject}*

{body}


_Number of attachments is {attachment_count}_
"""
