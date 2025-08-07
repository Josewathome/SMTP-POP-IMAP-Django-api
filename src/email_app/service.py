import os
import base64
import imaplib
import poplib
import email
import quopri
from django.core.mail import EmailMessage
from django.conf import settings
from typing import List, Optional, Dict, Union, Any
from django.core.mail import EmailMessage, get_connection
from email.header import decode_header

# Enhanced service.py
import mimetypes
import logging
from typing import Dict, List, Union, Any, Optional, Tuple
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import smtplib
import socket

logger = logging.getLogger(__name__)

class EmailServiceError(Exception):
    """Custom exception for email service errors"""
    pass

class EmailService:
    """Enhanced email service with comprehensive error handling and validation"""
    
    @staticmethod
    def to_bool(val: Union[str, bool]) -> bool:
        """Convert string or boolean to boolean value"""
        if isinstance(val, str):
            return val.lower() in ('true', '1', 'yes', 'on')
        return bool(val)
    
    @staticmethod
    def validate_email_addresses(emails: List[str]) -> Tuple[bool, List[str]]:
        """Validate a list of email addresses"""
        invalid_emails = []
        for email in emails:
            try:
                validate_email(email)
            except ValidationError:
                invalid_emails.append(email)
        return len(invalid_emails) == 0, invalid_emails
    
    @staticmethod
    def validate_attachment(attachment: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate attachment structure and content"""
        required_fields = ['filename', 'content', 'content_type']
        
        for field in required_fields:
            if field not in attachment:
                return False, f"Missing required field: {field}"
        
        # Validate base64 content
        try:
            base64.b64decode(attachment['content'], validate=True)
        except Exception as e:
            return False, f"Invalid base64 content: {str(e)}"
        
        return True, ""
    
    @classmethod
    def send_email(
        cls,
        email_settings: Dict[str, Any] = None,
        sender: str = "",
        recipients: List[str] = None,
        subject: str = "",
        body: str = "",
        cc: List[str] = None,
        bcc: List[str] = None,
        attachments: List[Dict[str, Any]] = None,
        use_default_settings: bool = False,
        html_body: str = None
    ) -> Dict[str, Any]:
        """
        Enhanced email sending service with comprehensive error handling
        
        Returns:
            Dict containing success status, message, and additional info
        """
        try:
            # Initialize default values
            recipients = recipients or []
            cc = cc or []
            bcc = bcc or []
            attachments = attachments or []
            email_settings = email_settings or {}
            
            # Validate email addresses
            all_emails = recipients + cc + bcc + ([sender] if sender else [])
            is_valid, invalid_emails = cls.validate_email_addresses(all_emails)
            
            if not is_valid:
                return {
                    'success': False,
                    'error': 'INVALID_EMAIL_ADDRESSES',
                    'message': f'Invalid email addresses: {", ".join(invalid_emails)}',
                    'invalid_emails': invalid_emails
                }
            
            # Validate recipients
            if not recipients:
                return {
                    'success': False,
                    'error': 'NO_RECIPIENTS',
                    'message': 'At least one recipient is required'
                }
            
            # Validate sender
            if not sender:
                return {
                    'success': False,
                    'error': 'NO_SENDER',
                    'message': 'Sender email is required'
                }
            
            # Validate subject and body
            if not subject.strip():
                return {
                    'success': False,
                    'error': 'NO_SUBJECT',
                    'message': 'Email subject is required'
                }
            
            # Check if we have meaningful content (either body or html_body)
            has_text_body = body and body.strip()
            has_html_body = html_body and html_body.strip()
            
            if not has_text_body and not has_html_body:
                return {
                    'success': False,
                    'error': 'NO_CONTENT',
                    'message': 'Either body or html_body content is required'
                }
            
            # Create email backend
            if use_default_settings:
                backend = EmailBackend()
            else:
                if not email_settings:
                    return {
                        'success': False,
                        'error': 'NO_EMAIL_SETTINGS',
                        'message': 'Email settings are required when not using default settings'
                    }
                
                # Validate required email settings
                required_settings = ['host', 'port', 'username', 'password']
                missing_settings = [s for s in required_settings if not email_settings.get(s)]
                
                if missing_settings:
                    return {
                        'success': False,
                        'error': 'MISSING_EMAIL_SETTINGS',
                        'message': f'Missing required email settings: {", ".join(missing_settings)}',
                        'missing_settings': missing_settings
                    }
                
                # Create custom backend
                backend = EmailBackend(
                    host=email_settings['host'],
                    port=int(email_settings['port']),
                    username=email_settings['username'],
                    password=email_settings['password'],
                    use_tls=cls.to_bool(email_settings.get('use_tls', False)),
                    use_ssl=cls.to_bool(email_settings.get('use_ssl', False)),
                    timeout=int(email_settings.get('timeout', 300))
                )
            
            # Create email message with proper body handling
            # Use text body if available and not empty, otherwise use empty string
            email_body = body.strip() if body and body.strip() else ""
            
            email_message = EmailMultiAlternatives(
                subject=subject,
                body=email_body,
                from_email=sender,
                to=recipients,
                cc=cc,
                bcc=bcc,
                connection=backend
            )
            
            # Add HTML alternative if provided and not empty
            if html_body and html_body.strip():
                email_message.attach_alternative(html_body.strip(), "text/html")
            
            # Process attachments
            processed_attachments = 0
            attachment_errors = []
            
            for i, attachment in enumerate(attachments):
                is_valid, error_msg = cls.validate_attachment(attachment)
                if not is_valid:
                    attachment_errors.append(f"Attachment {i+1}: {error_msg}")
                    continue
                
                try:
                    # Decode base64 content
                    file_content = base64.b64decode(attachment['content'])
                    
                    # Create attachment
                    email_message.attach(
                        attachment['filename'],
                        file_content,
                        attachment.get('content_type', 'application/octet-stream')
                    )
                    processed_attachments += 1
                    
                except Exception as e:
                    attachment_errors.append(f"Attachment {i+1} ({attachment.get('filename', 'unknown')}): {str(e)}")
            
            # Send email
            try:
                sent_count = email_message.send()
                
                result = {
                    'success': True,
                    'message': 'Email sent successfully',
                    'sent_count': sent_count,
                    'recipients_count': len(recipients),
                    'cc_count': len(cc),
                    'bcc_count': len(bcc),
                    'attachments_processed': processed_attachments,
                    'total_attachments': len(attachments)
                }
                
                if attachment_errors:
                    result['attachment_warnings'] = attachment_errors
                
                return result
                
            except smtplib.SMTPAuthenticationError:
                return {
                    'success': False,
                    'error': 'SMTP_AUTH_ERROR',
                    'message': 'SMTP authentication failed. Check username and password.'
                }
            
            except smtplib.SMTPRecipientsRefused as e:
                return {
                    'success': False,
                    'error': 'SMTP_RECIPIENTS_REFUSED',
                    'message': 'SMTP server refused recipients',
                    'refused_recipients': list(e.recipients.keys())
                }
            
            except smtplib.SMTPServerDisconnected:
                return {
                    'success': False,
                    'error': 'SMTP_SERVER_DISCONNECTED',
                    'message': 'SMTP server disconnected unexpectedly'
                }
            
            except smtplib.SMTPConnectError:
                return {
                    'success': False,
                    'error': 'SMTP_CONNECT_ERROR',
                    'message': 'Could not connect to SMTP server'
                }
            
            except socket.timeout:
                return {
                    'success': False,
                    'error': 'SMTP_TIMEOUT',
                    'message': 'SMTP connection timed out'
                }
            
            except Exception as e:
                logger.error(f"Unexpected error sending email: {str(e)}")
                return {
                    'success': False,
                    'error': 'UNEXPECTED_ERROR',
                    'message': f'An unexpected error occurred: {str(e)}'
                }
        
        except Exception as e:
            logger.error(f"Email service error: {str(e)}")
            return {
                'success': False,
                'error': 'SERVICE_ERROR',
                'message': f'Email service error: {str(e)}'
            }







max_emails = int(os.getenv('MAX_EMAILS'))
class EmailReceiver:
    @staticmethod
    def _decode_subject(subject):
        if subject is None:
            return ""
        decoded_parts = []
        for part, encoding in decode_header(subject):
            if isinstance(part, bytes):
                decoded_part = part.decode(encoding or 'utf-8', errors='ignore')
            else:
                decoded_part = part
            decoded_parts.append(decoded_part)
        return ' '.join(decoded_parts)

    @staticmethod
    def _decode_body(payload, content_type):
        try:
            if content_type == 'base64':
                return base64.b64decode(payload).decode('utf-8', errors='ignore')
            elif content_type == 'quoted-printable':
                return quopri.decodestring(payload).decode('utf-8', errors='ignore')
            return payload.decode('utf-8', errors='ignore')
        except Exception:
            return payload

    @staticmethod
    def receive_emails(email_config: Dict[str, Union[str, int, bool]], use_default_settings: bool = False) -> Dict[str, Any]:
        try:
            if use_default_settings:
                email_config = {
                    'host': os.getenv('EMAIL_HOST', 'imap.gmail.com'),
                    'port': int(os.getenv('EMAIL_PORT', 993)),
                    'username': os.getenv('EMAIL_HOST_USER', 'your_username'),
                    'password': os.getenv('EMAIL_HOST_PASSWORD', 'your_password'),
                    'use_ssl': os.getenv('EMAIL_USE_SSL', 'True') == 'True',
                    'use_tls': os.getenv('EMAIL_USE_TLS', 'True') == 'True',
                    'max_emails': max_emails,
                    'folder' : 'INBOX',
                    'protocol': 'IMAP' 
                }
                
            required_keys = ['host', 'port', 'username', 'password', 'use_ssl','use_tls', 'max_emails', 'protocol', 'folder']
            if not all(key in email_config for key in required_keys):
                return {"success": False, "message": "Missing required email configuration t"}
            use_ssl = email_config['use_ssl']
            use_tls = email_config['use_tls']
            if email_config['protocol'].upper() == 'IMAP':
                if use_ssl:
                    mail = imaplib.IMAP4_SSL(email_config['host'], email_config['port'])
                else:
                    mail = imaplib.IMAP4(email_config['host'], email_config['port'])
                mail.login(email_config['username'], email_config['password'])
                mail.select(f'{email_config["folder"]}')

                # Fetch emails
                _, search_data = mail.search(None, 'ALL')
                email_ids = search_data[0].split()[::-1][:email_config['max_emails']] 
                parsed_emails = []

                for num in email_ids:
                    _, data = mail.fetch(num, '(RFC822)')
                    raw_email = data[0][1]
                    email_message = email.message_from_bytes(raw_email)
                    email_details = {
                        'message_id': email_message.get('Message-ID', ''),
                        'subject': EmailReceiver._decode_subject(email_message.get('Subject', '')),
                        'from': email_message.get('From', ''),
                        'to': email_message.get('To', ''),
                        'date': email_message.get('Date', ''),
                        'body': '',
                        'html_body': '',
                        'attachments': []
                    }

                    for part in email_message.walk():
                        content_type = part.get_content_type()
                        if content_type == 'text/plain':
                            email_details['body'] = EmailReceiver._decode_body(part.get_payload(decode=True), part.get('Content-Transfer-Encoding', '').lower())
                        elif content_type == 'text/html':
                            email_details['html_body'] = EmailReceiver._decode_body(part.get_payload(decode=True), part.get('Content-Transfer-Encoding', '').lower())
                        elif part.get_filename():
                            filename = EmailReceiver._decode_subject(part.get_filename())
                            email_details['attachments'].append({
                                'filename': filename,
                                'content': base64.b64encode(part.get_payload(decode=True)).decode('utf-8'),
                                'mimetype': part.get_content_type()
                            })

                    parsed_emails.append(email_details)

                mail.close()
                mail.logout()

            elif email_config['protocol'].upper() == 'POP':
                if use_ssl:
                    mail = poplib.POP3_SSL(email_config['host'], email_config['port'])
                else:
                    mail = poplib.POP3(email_config['host'], email_config['port'])
                mail.user(email_config['username'])
                mail.pass_(email_config['password'])
                num_messages = len(mail.list()[1])
                parsed_emails = []
                for i in range(min(num_messages, email_config['max_emails'])):
                    response, raw_email, size = mail.retr(i + 1)
                    raw_email = b'\n'.join(raw_email)
                    email_message = email.message_from_bytes(raw_email)
                    email_details = {
                        'message_id': email_message.get('Message-ID', ''),
                        'subject': EmailReceiver._decode_subject(email_message.get('Subject', '')),
                        'from': email_message.get('From', ''),
                        'to': email_message.get('To', ''),
                        'date': email_message.get('Date', ''),
                        'body': '',
                        'html_body': '',
                        'attachments': []
                    }

                    for part in email_message.walk():
                        content_type = part.get_content_type()
                        if content_type == 'text/plain':
                            email_details['body'] = EmailReceiver._decode_body(part.get_payload(decode=True), part.get('Content-Transfer-Encoding', '').lower())
                        elif content_type == 'text/html':
                            email_details['html_body'] = EmailReceiver._decode_body(part.get_payload(decode=True), part.get('Content-Transfer-Encoding', '').lower())
                        elif part.get_filename():
                            filename = EmailReceiver._decode_subject(part.get_filename())
                            email_details['attachments'].append({
                                'filename': filename,
                                'content': base64.b64encode(part.get_payload(decode=True)).decode('utf-8'),
                                'mimetype': part.get_content_type()
                            })

                    parsed_emails.append(email_details)

                mail.quit()

            return {"success": True, "emails": parsed_emails}

        except Exception as e:
            return {"success": False, "message": str(e)}
