# Email to Telegram Forwarder

This project forwards unread emails to a specified Telegram chat.

## Features

- Checks for unread emails at regular intervals
- Forwards email content including subject, sender, and body to Telegram
- Handles attachments (counts them)
- Respects Telegram's message length limits
- Logs processed emails and any errors

## Requirements

- Python 3.7+
- Poetry for dependency management

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/zlochina/email-to-telegram.git
   cd email-to-telegram
   ```

2. Install dependencies using Poetry:
   ```
   poetry install
   ```

## Configuration

Edit `config.py` and set the following variables:

- `EMAIL`: Your email address
- `PASSWORD`: Your email password
- `IMAP_SERVER`: Your IMAP server address
- `IMAP_PORT`: Your IMAP server port (usually 993 for SSL)
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `TELEGRAM_CHAT_ID`: Your Telegram chat ID
- `RETRY_TIME`: Time in seconds between email checks
- `MESSAGE_PARSE_MODE`: Parsing mode set to Telegram message (Default value: "HTML")

## Usage

Run the script using Poetry:

```
poetry run python email_to_telegram.py
```

The script will run continuously, checking for new emails at the interval specified by `RETRY_TIME`.

## Logging

The script logs its activity to the console and to a file named `email_checker.log`. Check this file for information about processed emails and any errors that occur.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
