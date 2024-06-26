import email
import imaplib
import time
from email.header import decode_header
from email.utils import parseaddr, parsedate_to_datetime

import requests

from config import *


# Helper function for date formatting
def format_date(date_obj, format_string="%d/%m/%Y %H:%M"):
    return date_obj.strftime(format_string)


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    response = requests.post(url, data=data)
    return response.json()


def decode_subject(subject):
    decoded_subject, encoding = decode_header(subject)[0]
    if isinstance(decoded_subject, bytes):
        return decoded_subject.decode(encoding or "utf-8")
    return decoded_subject


def decode_content(content, default_charset="utf-8"):
    if isinstance(content, str):
        return content
    elif isinstance(content, bytes):
        try:
            return content.decode(default_charset)
        except UnicodeDecodeError:
            try:
                return content.decode("latin-1")
            except UnicodeDecodeError:
                return content.decode("ascii", errors="ignore")
    else:
        return str(content)


def check_emails():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")

    _, search_data = mail.search(None, "UNSEEN")
    for num in search_data[0].split():
        _, msg_data = mail.fetch(num, "(RFC822)")
        email_body = msg_data[0][1]
        email_message = email.message_from_bytes(email_body)

        subject = decode_subject(email_message["Subject"])
        sender_name, sender_address = parseaddr(email_message["From"])
        date = parsedate_to_datetime(email_message["Date"])

        body = ""
        attachment_count = 0
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or "utf-8"
                    body += decode_content(payload, charset)
                elif (
                    part.get_content_maintype() != "multipart"
                    and part.get("Content-Disposition") is not None
                ):
                    attachment_count += 1
        else:
            payload = email_message.get_payload(decode=True)
            charset = email_message.get_content_charset() or "utf-8"
            body += decode_content(payload, charset)

        message = MESSAGE_TEMPLATE.format(
            date=format_date(date),
            sender_name=sender_name or "Unknown",
            sender_address=sender_address,
            subject=subject,
            body=body,
            attachment_count=attachment_count,
        )
        send_telegram_message(message)

    mail.close()
    mail.logout()


if __name__ == "__main__":
    while True:
        check_emails()
        time.sleep(RETRY_TIME)  # Check every 60 seconds
