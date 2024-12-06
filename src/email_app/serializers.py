from rest_framework import serializers
from typing import Dict, Union, List, Optional

class EmailSerializer(serializers.Serializer):
    # Email settings configuration
    email_settings = serializers.DictField(
        child=serializers.CharField(),
        required=False,
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
        help_text="List of recipient email addresses"
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
        help_text="Email subject"
    )
    
    body = serializers.CharField(
        required=True,
        help_text="Email body content"
    )
    
    # Attachments
    attachments = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True,
        help_text="Optional list of file attachments (base64 encoded)"
    )
    
    # Default settings flag
    use_default_settings = serializers.BooleanField(
        default=False,
        help_text="Use Django's default email settings"
    )
    
    def validate(self, data):
        """
        Additional validation for email data
        """
        # Add custom validation logic if needed
        if not data.get('use_default_settings') and not data.get('email_settings'):
            raise serializers.ValidationError(
                "Email settings are required when not using default settings"
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