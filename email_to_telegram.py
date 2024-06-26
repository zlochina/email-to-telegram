import email
import imaplib
import logging
import time
from email.header import decode_header
from email.utils import parseaddr, parsedate_to_datetime

import requests

from config import *

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


# Helper function for date formatting
def format_date(date_obj, format_string="%d/%m/%Y %H:%M"):
    return date_obj.strftime(format_string)


# Helper function for splitting telegram message
def split_message(message, max_length=4095):
    parts = []
    while len(message) > max_length:
        part = message[:max_length]
        last_newline = part.rfind("\n")
        if last_newline != -1:
            parts.append(message[:last_newline])
            message = message[last_newline + 1 :]
        else:
            parts.append(part)
            message = message[max_length:]
    parts.append(message)
    return parts


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    responses = []
    for part in split_message(message):
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": part, "parse_mode": "Markdown"}
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            responses.append(response.json())
            if not response.json().get("ok"):
                logging.error(f"Failed to send message: {response.json()}")
        except requests.RequestException as e:
            logging.error(f"Error sending message: {str(e)}")
    return responses


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

        # Log the processed email
        logging.info(
            f"Processed email: Date: {format_date(date)}, From: {sender_name} ({sender_address}), Subject: {subject}"
        )

    mail.close()
    mail.logout()


if __name__ == "__main__":
    logging.info("Starting email checking script")
    while True:
        try:
            check_emails()
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
        logging.info(f"Sleeping for {RETRY_TIME} seconds")
        time.sleep(RETRY_TIME)
