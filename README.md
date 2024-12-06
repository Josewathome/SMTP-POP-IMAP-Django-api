# Django Email Service API

## Project Overview

This Django-based Email Service API provides a robust and flexible solution for sending and receiving emails through a RESTful interface. The project supports advanced email operations, including:
- Sending emails with comprehensive configuration options
- Receiving the most recent emails from an IMAP or POP server
- Support for attachments
- Flexible SMTP and IMAP & POP server configurations

## Features

- 🚀 **Flexible Email Sending**
  - Multiple recipients support
  - CC and BCC functionality
  - Custom SMTP server configuration
  - Attachment handling

- 📨 **Comprehensive Email Receiving**
  - Retrieve most recent emails
  - Configurable email count
  - Full email details extraction
  - Supports various email encodings

- 🔒 **Secure Configuration**
  - Environment variable support
  - Configurable SSL/TLS connections
  - Flexible server settings

## Prerequisites

- Python 3.9+
- Docker (optional, but recommended)
- SMTP and IMAP and POP server credentials

## Installation Methods

### 1. Local Development Setup

#### Clone the Repository
```bash
git clone https://github.com/Josewathome/SMTP-POP-IMAP-Django-api.git
cd SMTP-POP-IMAP-Django-api
```

#### Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Configure Environment
Create a `.env` file with your configurations:
```
ALLOWED_HOSTS=localhost,127.0.0.1 <for deployment add the allowed hosts>
SECRET_KEY=your_secret_key
DEBUG=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
JWT_ACCESS_TOKEN=your-uniqueverification-beara-code example: djduey67*************hsi

MAX_EMAILS=<the defult number of emails you want to pull as integer>
```

#### Run Migrations
```bash
python manage.py migrate
```

#### Start Development Server
```bash
python manage.py runserver
```

### 2. Docker Deployment

#### Build and Run with Docker Compose
```bash
docker-compose up --build
```

## API Endpoints

### 1. Send Email Endpoint
**URL:** `/api/email/send/`
**Method:** `POST`

#### Payload Scenarios

1. **Basic Email with Default Settings**
```json
{
    "sender": "sender@example.com",
    "recipients": ["recipient@example.com"],
    "subject": "Hello World",
    "body": "This is a test email",
    "use_default_settings": true
}
```

2. **Email with Custom SMTP and Attachments**
```json
{
    "email_settings": {
        "host": "smtp.gmail.com",
        "port": 587,
        "username": "your_email@gmail.com",
        "password": "your_app_password",
        "use_tls": "False",
		"use_ssl" : "True"
    },
    "sender": "sender@example.com",
    "recipients": ["recipient1@example.com", "recipient2@example.com"],
    "cc": ["cc@example.com"],
    "bcc": ["bcc@example.com"],
    "subject": "Email with Attachment",
    "body": "Please find the attached document",
    "attachments": [
        {
            "filename": "document.pdf",
            "content": "base64_encoded_pdf_content",
            "mimetype": "application/pdf"
        }
    ],
    "use_default_settings": false
}
```

### 2. Receive Email Endpoint
**URL:** `/api/email/receive/`
**Method:** `POST`

#### Payload Scenarios

1. **Retrieve Latest 2 Emails**
```json
{
    "host": "imap.gmail.com",
    "username": "your_email@gmail.com",
    "password": "your_app_password",
    "max_emails": 2,
    "port": 934,
    "use_tls": false,
    "use_ssl" : true,
    "folder": "INBOX",
    "max_emails": 2,
    "protocol": "IMAP" // Or 'POP'
}
```

#### Expected Response Formats

**Successful Send Email Response:**
```json
{
    "success": true,
    "message": "Email sent successfully"
}
```

**Successful Receive Email Response:**
```json
{
    "success": true,
    "emails": [
        {
            "message_id": "<unique_id>",
            "subject": "Email Subject",
            "from": "sender@example.com",
            "to": "recipient@example.com",
            "date": "Timestamp",
            "body": "Plain text email content",
            "html_body": "<html>HTML content</html>",
            "attachments": [
                {
                    "filename": "attachment.pdf",
                    "content": "base64_encoded_content",
                    "mimetype": "application/pdf"
                }
            ]
        }
    ]
}
```

## Security Considerations

- Use App Passwords for Gmail and other providers
- Never commit sensitive credentials to version control
- Use environment variables for configuration
- Implement additional authentication for production

## Troubleshooting

1. **SMTP Connection Issues**
   - Verify credentials
   - Check firewall settings
   - Ensure app passwords are used

2. **Email Retrieval Problems**
   - Confirm IMAP settings
   - Check server-specific configurations
   - Verify network connectivity

## Performance Optimization

- Use connection pooling for email servers
- Implement caching mechanisms
- Set reasonable timeouts

## Logging

Configure logging in `settings.py` to track email operations and debug issues.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Specify your project's license]

## Support

For issues or questions, please open a GitHub issue or contact [your contact information].

## Disclaimer

This email service is provided as-is. Always test thoroughly in a controlled environment before production use.
```
