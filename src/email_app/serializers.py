from rest_framework import serializers
from typing import Dict, Union, List, Optional
import base64

class EmailSerializer(serializers.Serializer):
    """Enhanced email serializer with comprehensive validation"""
    
    # Email settings configuration
    email_settings = serializers.DictField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True,
        help_text="SMTP server configuration settings"
    )
    
    # Sender configuration
    sender = serializers.EmailField(
        required=True,
        help_text="Sender's email address"
    )
    
    # Recipients configuration
    recipients = serializers.ListField(
        child=serializers.EmailField(),
        required=True,
        min_length=1,
        help_text="List of recipient email addresses (at least one required)"
    )
    
    # Optional CC and BCC
    cc = serializers.ListField(
        child=serializers.EmailField(),
        required=False,
        allow_empty=True,
        help_text="Optional list of CC recipients"
    )
    
    bcc = serializers.ListField(
        child=serializers.EmailField(),
        required=False,
        allow_empty=True,
        help_text="Optional list of BCC recipients"
    )
    
    # Email content
    subject = serializers.CharField(
        required=True,
        min_length=1,
        max_length=998,  # RFC 5322 limit
        help_text="Email subject (1-998 characters)"
    )
    
    body = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Email body content (plain text)"
    )
    
    html_body = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Email body content (HTML format)"
    )
    
    # Attachments
    attachments = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True,
        max_length=10,  # Limit number of attachments
        help_text="Optional list of file attachments (max 10)"
    )
    
    # Default settings flag
    use_default_settings = serializers.BooleanField(
        default=False,
        help_text="Use Django's default email settings"
    )
    
    def validate_email_settings(self, value):
        """Validate email settings structure"""
        if not value:
            return value
        
        # Check for required fields when custom settings are provided
        if not self.initial_data.get('use_default_settings', False):
            required_fields = ['host', 'port', 'username', 'password']
            missing_fields = [field for field in required_fields if not value.get(field)]
            
            if missing_fields:
                raise serializers.ValidationError(
                    f"Missing required email settings: {', '.join(missing_fields)}"
                )
        
        # Validate port
        if 'port' in value:
            try:
                port = int(value['port'])
                if not (1 <= port <= 65535):
                    raise serializers.ValidationError("Port must be between 1 and 65535")
            except (ValueError, TypeError):
                raise serializers.ValidationError("Port must be a valid integer")
        
        return value
    
    def validate_attachments(self, value):
        """Validate attachments structure and content"""
        if not value:
            return value
        
        total_size = 0
        max_attachment_size = 25 * 1024 * 1024  # 25MB per attachment
        max_total_size = 100 * 1024 * 1024  # 100MB total
        
        for i, attachment in enumerate(value):
            # Check required fields
            required_fields = ['filename', 'content', 'content_type']
            missing_fields = [field for field in required_fields if field not in attachment]
            
            if missing_fields:
                raise serializers.ValidationError(
                    f"Attachment {i+1} missing required fields: {', '.join(missing_fields)}"
                )
            
            # Validate filename
            if not attachment['filename'].strip():
                raise serializers.ValidationError(f"Attachment {i+1} filename cannot be empty")
            
            # Validate base64 content
            try:
                content = base64.b64decode(attachment['content'], validate=True)
                content_size = len(content)
                
                if content_size > max_attachment_size:
                    raise serializers.ValidationError(
                        f"Attachment {i+1} exceeds maximum size of 25MB"
                    )
                
                total_size += content_size
                
            except Exception as e:
                raise serializers.ValidationError(
                    f"Attachment {i+1} has invalid base64 content: {str(e)}"
                )
        
        if total_size > max_total_size:
            raise serializers.ValidationError(
                f"Total attachments size exceeds maximum of 100MB"
            )
        
        return value
    
    def validate(self, data):
        """Additional validation for email data"""
        # Validate that we have meaningful content (either body or html_body)
        body = data.get('body', '').strip() if data.get('body') else ''
        html_body = data.get('html_body', '').strip() if data.get('html_body') else ''
        
        if not body and not html_body:
            raise serializers.ValidationError(
                "Either 'body' or 'html_body' must be provided and not empty"
            )
        
        # Validate email settings requirement
        if not data.get('use_default_settings') and not data.get('email_settings'):
            raise serializers.ValidationError(
                "Email settings are required when not using default settings"
            )
        
        # Validate TLS/SSL settings
        email_settings = data.get('email_settings', {})
        if email_settings:
            use_tls = email_settings.get('use_tls', 'false').lower() == 'true'
            use_ssl = email_settings.get('use_ssl', 'false').lower() == 'true'
            
            if use_tls and use_ssl:
                raise serializers.ValidationError(
                    "Cannot use both TLS and SSL simultaneously. Choose one."
                )
        
        return data
    
from rest_framework import serializers
from typing import Dict, Union

from rest_framework import serializers
from typing import Dict, Union

class EmailReceiveSerializer(serializers.Serializer):
    # Email server configuration
    host = serializers.CharField(
        required=True,
        help_text="IMAP server hostname"
    )
    
    username = serializers.EmailField(
        required=True,
        help_text="Email account username"
    )
    
    password = serializers.CharField(
        required=True,
        help_text="Email account password",
        style={'input_type': 'password'}
    )
    
    port = serializers.IntegerField(
        required=False,
        default=993,
        help_text="IMAP server port (default: 993)"
    )
    
    use_ssl = serializers.BooleanField(
        required=False,
        default=True,
        help_text="Use SSL for connection"
    )
    
    folder = serializers.CharField(
        required=False,
        default='INBOX',
        help_text="Email folder to retrieve emails from"
    )
    
    max_emails = serializers.IntegerField(
        required=True,
        min_value=1,
        max_value=100,
        help_text="Maximum number of most recent emails to retrieve"
    )

    def validate(self, data):
        """
        Additional validation for email receive configuration
        """
        # Ensure max_emails is a positive integer
        if 'max_emails' not in data or data['max_emails'] < 1:
            raise serializers.ValidationError({
                "max_emails": "Must be a positive integer"
            })
        
        return data