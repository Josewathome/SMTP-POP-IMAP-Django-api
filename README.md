
# Django Email Service API

A production-ready Django backend for sending and receiving emails via REST APIs. Designed for reliability, flexibility, and operational visibility in real-world SaaS systems.

---

## Key Capabilities

- **Email Sending**
  - Multi-recipient, CC/BCC support
  - Attachment handling
  - Custom SMTP configuration per request
  - TLS/SSL options
- **Email Retrieval**
  - IMAP and POP support
  - Fetch configurable number of recent emails
  - Returns full metadata and content (plain text + HTML)
- **Security & Operations**
  - JWT-protected endpoints
  - Environment-based configuration
  - Connection pooling and timeout control
  - Logging and error tracking for all operations

---

## Architecture & Design Notes

- Built with **Django REST Framework** for robust, maintainable APIs.
- **Asynchronous processing** used for sending bulk emails to avoid blocking requests.
- **Flexible backend**: Each request can override default SMTP/IMAP settings, allowing multi-tenant use cases.
- **Operational safety**:
  - All credentials stored in environment variables
  - App passwords recommended for Gmail/third-party providers
  - Logs structured for traceability
- Designed to run in **Docker** or bare Python environments for maximum portability.
- Endpoint payloads validated to prevent injection, misrouting, or attachment misuse.

---

## Quick Start

### Local Development
```bash
git clone https://github.com/Josewathome/SMTP-POP-IMAP-Django-api.git
cd SMTP-POP-IMAP-Django-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
````

Configure `.env` with your SMTP/IMAP credentials and JWT key.

### Docker

```bash
docker-compose up --build
```

---

## API Endpoints

### Send Email

**POST** `/api/email/send/`

Supports:

* Default SMTP settings
* Per-request custom SMTP configuration
* Attachments

**Example Payload:**

```json
{
  "sender": "sender@example.com",
  "recipients": ["recipient@example.com"],
  "subject": "Hello",
  "body": "Test email",
  "use_default_settings": true
}
```

**Response:**

```json
{"success": true, "message": "Email sent successfully"}
```

### Receive Email

**POST** `/api/email/receive/`

Supports:

* IMAP or POP protocol
* Fetch configurable number of latest emails
* Returns metadata, body, HTML, attachments

**Example Payload:**

```json
{
  "host": "imap.gmail.com",
  "username": "your_email@gmail.com",
  "password": "app_password",
  "max_emails": 5,
  "protocol": "IMAP",
  "folder": "INBOX"
}
```

**Response:**

```json
{
  "success": true,
  "emails": [
    {
      "subject": "Email Subject",
      "from": "sender@example.com",
      "to": "recipient@example.com",
      "body": "Plain text",
      "html_body": "<html>HTML</html>",
      "attachments": []
    }
  ]
}
```

---

## Operational Notes

* **Logging**: All operations logged for traceability.
* **Performance**: Connection pooling, caching, and request timeouts implemented.
* **Security**: Never commit credentials; JWT auth and environment variables used.

---

## Why This Exists

This is not a tutorial or boilerplate. Built to replace fragile email workflows in production SaaS apps, supporting multi-tenant setups, attachments, dynamic SMTP configuration, and operational visibility. Used in live systems with high-volume email traffic.

---
