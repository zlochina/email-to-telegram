import email
import imaplib
import time
from email.header import decode_header

import requests

from config import *


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
        sender = email.utils.parseaddr(email_message["From"])[1]

        message = f"<b>New Email</b>\n\nFrom: {sender}\nSubject: {subject}\n\n"

        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    message += part.get_payload(decode=True).decode()
        else:
            message += email_message.get_payload(decode=True).decode()

        send_telegram_message(message)

    mail.close()
    mail.logout()


if __name__ == "__main__":
    while True:
        check_emails()
        time.sleep(RETRY_TIME)  # Check every 60 seconds
