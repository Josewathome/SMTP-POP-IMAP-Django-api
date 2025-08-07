# Email Service API Documentation

## Overview
The Email Service API provides endpoints for sending emails with support for HTML content, attachments, CC/BCC recipients, and custom SMTP configurations.

## Base URL
```
/api/
```

## Endpoints

### 1. Send Email
**Endpoint:** `POST /send/`  
**Description:** Send an email with optional attachments and custom SMTP settings

#### Request Payload Options

##### Option 1: Using Default Django Email Settings
```json
{
    "use_default_settings": true,
    "sender": "sender@example.com",
    "recipients": ["recipient1@example.com", "recipient2@example.com"],
    "subject": "Test Email Subject",
    "body": "This is the plain text body of the email.",
    "html_body": "<h1>HTML Email</h1><p>This is the HTML body.</p>",
    "cc": ["cc@example.com"],
    "bcc": ["bcc@example.com"]
}

body and html_body either can be emty strings
```
// Scenario 1: HTML only
{
  "body": "",
  "html_body": "<h1>Hello!</h1>"
}

// Scenario 2: Plain text only  
{
  "body": "Hello!",
  "html_body": ""
}

// Scenario 3: Both (recommended)
{
  "body": "Hello!",
  "html_body": "<h1>Hello!</h1>"
}

// Scenario 4: Invalid - both empty
{
  "body": "",
  "html_body": ""
}  // Returns validation error

##### Option 2: Using Custom SMTP Settings
```json
{
    "use_default_settings": false,
    "email_settings": {
        "host": "smtp.gmail.com",
        "port": "587",
        "username": "your-email@gmail.com",
        "password": "your-app-password",
        "use_tls": "true",
        "use_ssl": "false",
        "timeout": "300"
    },
    "sender": "sender@example.com",
    "recipients": ["recipient1@example.com"],
    "subject": "Custom SMTP Email",
    "body": "Email sent via custom SMTP configuration."
}
```

##### Option 3: Email with Attachments
```json
{
    "use_default_settings": true,
    "sender": "sender@example.com",
    "recipients": ["recipient@example.com"],
    "subject": "Email with Attachments",
    "body": "Please find the attached files.",
    "attachments": [
        {
            "filename": "document.pdf",
            "content": "JVBERi0xLjQKJcfsj6IKNSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMC=",
            "content_type": "application/pdf"
        },
        {
            "filename": "image.png",
            "content": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
            "content_type": "image/png"
        }
    ]
}
```

##### Option 4: Minimal Required Payload
```json
{
    "use_default_settings": true,
    "sender": "sender@example.com",
    "recipients": ["recipient@example.com"],
    "subject": "Minimal Email",
    "body": "This is a minimal email."
}
```

#### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `use_default_settings` | boolean | No (default: false) | Whether to use Django's default email configuration |
| `email_settings` | object | Conditional* | Custom SMTP server configuration |
| `sender` | string (email) | Yes | Sender's email address |
| `recipients` | array[string] | Yes | List of recipient email addresses (min: 1) |
| `cc` | array[string] | No | List of CC recipients |
| `bcc` | array[string] | No | List of BCC recipients |
| `subject` | string | Yes | Email subject (1-998 characters) |
| `body` | string | Conditional** | Plain text email body |
| `html_body` | string | Conditional** | HTML email body |
| `attachments` | array[object] | No | List of file attachments (max: 10) |

*Required when `use_default_settings` is false  
**Either `body` or `html_body` must be provided

#### Email Settings Object
```json
{
    "host": "smtp.server.com",        // SMTP server hostname
    "port": "587",                    // SMTP server port (1-65535)
    "username": "user@example.com",   // SMTP username
    "password": "password",           // SMTP password
    "use_tls": "true",               // Use TLS encryption
    "use_ssl": "false",              // Use SSL encryption
    "timeout": "300"                 // Connection timeout in seconds
}
```

#### Attachment Object
```json
{
    "filename": "document.pdf",       // File name with extension
    "content": "base64-encoded-data", // Base64 encoded file content
    "content_type": "application/pdf" // MIME type of the file
}
```

#### Response Formats

##### Success Response (200 OK)
```json
{
    "success": true,
    "message": "Email sent successfully",
    "sent_count": 1,
    "recipients_count": 2,
    "cc_count": 1,
    "bcc_count": 1,
    "attachments_processed": 2,
    "total_attachments": 2
}
```

##### Success with Warnings (200 OK)
```json
{
    "success": true,
    "message": "Email sent successfully",
    "sent_count": 1,
    "recipients_count": 1,
    "cc_count": 0,
    "bcc_count": 0,
    "attachments_processed": 1,
    "total_attachments": 2,
    "attachment_warnings": [
        "Attachment 2: Invalid base64 content: Incorrect padding"
    ]
}
```

#### Error Responses

##### Validation Error (400 Bad Request)
```json
{
    "success": false,
    "error": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "validation_errors": {
        "recipients": ["This field is required."],
        "subject": ["This field may not be blank."]
    }
}
```

##### Invalid Email Addresses (400 Bad Request)
```json
{
    "success": false,
    "error": "INVALID_EMAIL_ADDRESSES",
    "message": "Invalid email addresses: invalid-email, another@invalid",
    "invalid_emails": ["invalid-email", "another@invalid"]
}
```

##### Missing Recipients (400 Bad Request)
```json
{
    "success": false,
    "error": "NO_RECIPIENTS",
    "message": "At least one recipient is required"
}
```

##### Missing Email Settings (400 Bad Request)
```json
{
    "success": false,
    "error": "MISSING_EMAIL_SETTINGS",
    "message": "Missing required email settings: host, port, username",
    "missing_settings": ["host", "port", "username"]
}
```

##### SMTP Authentication Error (401 Unauthorized)
```json
{
    "success": false,
    "error": "SMTP_AUTH_ERROR",
    "message": "SMTP authentication failed. Check username and password."
}
```

##### Recipients Refused (422 Unprocessable Entity)
```json
{
    "success": false,
    "error": "SMTP_RECIPIENTS_REFUSED",
    "message": "SMTP server refused recipients",
    "refused_recipients": ["blocked@example.com"]
}
```

##### SMTP Connection Error (503 Service Unavailable)
```json
{
    "success": false,
    "error": "SMTP_CONNECT_ERROR",
    "message": "Could not connect to SMTP server"
}
```

##### SMTP Timeout (504 Gateway Timeout)
```json
{
    "success": false,
    "error": "SMTP_TIMEOUT",
    "message": "SMTP connection timed out"
}
```

##### Internal Server Error (500 Internal Server Error)
```json
{
    "success": false,
    "error": "UNEXPECTED_ERROR",
    "message": "An unexpected error occurred: Connection refused"
}
```

### 2. Service Information
**Endpoint:** `GET /send/`  
**Description:** Get service information and health check

#### Response (200 OK)
```json
{
    "service": "Email Service API",
    "version": "1.0.0",
    "status": "active",
    "endpoints": {
        "send_email": {
            "method": "POST",
            "description": "Send email with attachments support",
            "max_recipients": 100,
            "max_attachments": 10,
            "max_attachment_size": "25MB",
            "max_total_attachment_size": "100MB"
        }
    }
}
```

## Complete Error Code Reference

| Error Code | HTTP Status | Description | Common Causes |
|------------|-------------|-------------|---------------|
| `VALIDATION_ERROR` | 400 | Request validation failed | Missing required fields, invalid data types |
| `INVALID_EMAIL_ADDRESSES` | 400 | One or more email addresses are invalid | Malformed email addresses |
| `NO_RECIPIENTS` | 400 | No recipients specified | Empty recipients array |
| `NO_SENDER` | 400 | No sender specified | Missing sender field |
| `NO_SUBJECT` | 400 | No subject specified | Empty or missing subject |
| `NO_CONTENT` | 400 | No email content | Both body and html_body are empty |
| `NO_EMAIL_SETTINGS` | 400 | Email settings required | Custom settings needed but not provided |
| `MISSING_EMAIL_SETTINGS` | 400 | Required email settings missing | Incomplete SMTP configuration |
| `SMTP_AUTH_ERROR` | 401 | SMTP authentication failed | Wrong username/password |
| `SMTP_RECIPIENTS_REFUSED` | 422 | Server refused recipients | Invalid/blocked email addresses |
| `SMTP_SERVER_DISCONNECTED` | 503 | SMTP server disconnected | Server connection issues |
| `SMTP_CONNECT_ERROR` | 503 | Cannot connect to SMTP server | Network/firewall issues |
| `SMTP_TIMEOUT` | 504 | SMTP connection timeout | Slow network/server response |
| `UNEXPECTED_ERROR` | 500 | Unexpected system error | Various system issues |
| `SERVICE_ERROR` | 500 | Email service error | Internal service problems |
| `INTERNAL_ERROR` | 500 | Internal server error | Unhandled exceptions |

## Usage Examples

### Example 1: Basic Email with Default Settings
```bash
curl -X POST http://localhost:8000/api/email/send/ \
  -H "Content-Type: application/json" \
  -d '{
    "use_default_settings": true,
    "sender": "noreply@mycompany.com",
    "recipients": ["user@example.com"],
    "subject": "Welcome to Our Service",
    "body": "Thank you for signing up!",
    "html_body": "<h1>Welcome!</h1><p>Thank you for signing up!</p>"
  }'
```

### Example 2: Gmail SMTP Configuration
```bash
curl -X POST http://localhost:8000/api/email/send/ \
  -H "Content-Type: application/json" \
  -d '{
    "use_default_settings": false,
    "email_settings": {
      "host": "smtp.gmail.com",
      "port": "587",
      "username": "your-email@gmail.com",
      "password": "your-app-password",
      "use_tls": "true",
      "use_ssl": "false"
    },
    "sender": "your-email@gmail.com",
    "recipients": ["recipient@example.com"],
    "subject": "Test from Gmail",
    "body": "This email was sent via Gmail SMTP."
  }'
```

### Example 3: Bulk Email with Attachments
```bash
curl -X POST http://localhost:8000/api/email/send/ \
  -H "Content-Type: application/json" \
  -d '{
    "use_default_settings": true,
    "sender": "newsletter@company.com",
    "recipients": [
      "user1@example.com",
      "user2@example.com",
      "user3@example.com"
    ],
    "cc": ["manager@company.com"],
    "bcc": ["archive@company.com"],
    "subject": "Monthly Report",
    "body": "Please find the monthly report attached.",
    "html_body": "<h2>Monthly Report</h2><p>Please find the monthly report attached.</p>",
    "attachments": [
      {
        "filename": "report.pdf",
        "content": "JVBERi0xLjQKJcfsj6IK...",
        "content_type": "application/pdf"
      }
    ]
  }'
```

## Best Practices

### 1. Email Address Validation
- Always validate email addresses before sending
- The API performs server-side validation, but client-side validation improves UX
- Use proper email regex patterns or validation libraries

### 2. SMTP Configuration Security
- Never hardcode SMTP credentials in your application
- Use environment variables or secure credential storage
- For Gmail, use App Passwords instead of regular passwords
- Consider using OAuth2 for production applications

### 3. Attachment Handling
- Encode files to base64 before sending
- Keep attachments under 25MB each
- Total attachment size should not exceed 100MB
- Always specify correct MIME types

### 4. Error Handling
- Implement proper error handling for all error codes
- Show user-friendly error messages
- Log errors for debugging purposes
- Implement retry logic for temporary failures

### 5. Rate Limiting
- Implement rate limiting to prevent abuse
- Consider SMTP provider limits (Gmail: 500 emails/day for free accounts)
- Use queuing systems for bulk emails

## Common SMTP Configurations

### Gmail
```json
{
    "host": "smtp.gmail.com",
    "port": "587",
    "use_tls": "true",
    "use_ssl": "false"
}
```

### Outlook/Hotmail
```json
{
    "host": "smtp-mail.outlook.com",
    "port": "587",
    "use_tls": "true",
    "use_ssl": "false"
}
```

### Yahoo Mail
```json
{
    "host": "smtp.mail.yahoo.com",
    "port": "587",
    "use_tls": "true",
    "use_ssl": "false"
}
```

### SendGrid
```json
{
    "host": "smtp.sendgrid.net",
    "port": "587",
    "username": "apikey",
    "password": "your-sendgrid-api-key",
    "use_tls": "true",
    "use_ssl": "false"
}
```

### Mailgun
```json
{
    "host": "smtp.mailgun.org",
    "port": "587",
    "use_tls": "true",
    "use_ssl": "false"
}
```

## Troubleshooting

### Common Issues and Solutions

1. **SMTP Authentication Failed**
   - Verify username and password
   - Check if 2FA is enabled (use app passwords)
   - Ensure "Less secure app access" is enabled (Gmail legacy)

2. **Connection Timeout**
   - Check firewall settings
   - Verify SMTP server hostname and port
   - Try different ports (587 for TLS, 465 for SSL, 25 for unencrypted)

3. **Recipients Refused**
   - Verify email addresses are valid
   - Check if recipients are blacklisted
   - Ensure sender reputation is good

4. **Attachment Issues**
   - Verify base64 encoding is correct
   - Check file size limits
   - Ensure MIME types are accurate

5. **HTML Email Not Displaying**
   - Validate HTML structure
   - Test across different email clients
   - Provide plain text fallback

## Security Considerations

1. **Credential Protection**
   - Store SMTP credentials securely
   - Use environment variables
   - Implement proper access controls

2. **Input Validation**
   - Validate all input data
   - Sanitize HTML content
   - Prevent email injection attacks

3. **Rate Limiting**
   - Implement API rate limiting
   - Monitor for suspicious activity
   - Set reasonable usage quotas

4. **Logging**
   - Log email sending attempts
   - Do not log sensitive information
   - Implement proper log rotation