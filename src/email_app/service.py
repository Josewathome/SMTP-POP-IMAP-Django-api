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


class EmailService:
    @staticmethod
    def send_email(
        email_settings: Dict[str, Union[str, bool]],
        sender: str,
        recipients: List[str],
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, str]]] = None,
        use_default_settings: bool = False
    ) -> Dict[str, Union[bool, str]]:
        """
        Send an email with flexible configuration options.

        :param email_settings: Dictionary containing SMTP settings
        :param sender: Sender's email address
        :param recipients: List of recipient email addresses
        :param subject: Email subject
        :param body: Email body
        :param cc: Optional list of CC recipients
        :param bcc: Optional list of BCC recipients
        :param attachments: Optional list of file attachments
        :param use_default_settings: Use Django's default email settings
        :return: Dictionary with send status and message
        """
        try:
            if not use_default_settings:
                required_keys = ['host', 'port', 'username', 'password', 'use_tls', 'use_ssl']
                if not all(key in email_settings for key in required_keys):
                    return {
                        "success": False, 
                        "message": "Missing required email settings"
                    }
                use_tls = email_settings['use_tls'] == "false" if isinstance(email_settings['use_tls'], str) else email_settings['use_tls']
                use_ssl = email_settings['use_ssl'] == "True" if isinstance(email_settings['use_ssl'], str) else email_settings['use_ssl']
                connection = get_connection(
                    host=email_settings['host'],
                    port=email_settings['port'],
                    username=email_settings['username'],
                    password=email_settings['password'],
                    use_tls=use_tls,
                    use_ssl=use_ssl,
                )
            else:
                connection = None
            email = EmailMessage(
                subject=subject,
                body=body,
                from_email=sender,
                to=recipients,
                cc=cc or [],
                bcc=bcc or [],
                connection=connection
            )
            if attachments:
                for attachment in attachments:
                    file_content = base64.b64decode(attachment['content']) if 'content' in attachment else None
                    if file_content:
                        email.attach(
                            filename=attachment.get('filename', 'attachment'),
                            content=file_content,
                            mimetype=attachment.get('mimetype', 'application/octet-stream')
                        )
            email.send()
            return {"success": True, "message": "Email sent successfully"}
        
        except Exception as e:
            return {"success": False, "message": str(e)}

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
