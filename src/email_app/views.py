from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import EmailSerializer, EmailReceiveSerializer
from .service import EmailReceiver ,EmailService, max_emails

from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
import logging

logger = logging.getLogger(__name__)

class SendEmailView(APIView):
    """Enhanced email sending API view with comprehensive error handling"""
    
    @method_decorator(never_cache)
    def post(self, request):
        """
        Send email with enhanced error handling and validation
        """
        try:
            serializer = EmailSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': 'VALIDATION_ERROR',
                    'message': 'Request validation failed',
                    'validation_errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            email_data = serializer.validated_data
            
            # Log email attempt (without sensitive data)
            logger.info(f"Email send attempt: {len(email_data['recipients'])} recipients, "
                       f"Subject: {email_data['subject'][:50]}...")
            
            # Send email using service
            result = EmailService.send_email(
                email_settings=email_data.get('email_settings', {}),
                sender=email_data['sender'],
                recipients=email_data['recipients'],
                subject=email_data['subject'],
                body=email_data.get('body', ''),
                html_body=email_data.get('html_body'),
                cc=email_data.get('cc', []),
                bcc=email_data.get('bcc', []),
                attachments=email_data.get('attachments', []),
                use_default_settings=email_data.get('use_default_settings', False)
            )
            
            # Log result
            if result['success']:
                logger.info(f"Email sent successfully to {result.get('recipients_count', 0)} recipients")
                return Response(result, status=status.HTTP_200_OK)
            else:
                logger.warning(f"Email send failed: {result.get('error', 'Unknown error')}")
                
                # Map error types to appropriate HTTP status codes
                error_status_map = {
                    'VALIDATION_ERROR': status.HTTP_400_BAD_REQUEST,
                    'INVALID_EMAIL_ADDRESSES': status.HTTP_400_BAD_REQUEST,
                    'NO_RECIPIENTS': status.HTTP_400_BAD_REQUEST,
                    'NO_SENDER': status.HTTP_400_BAD_REQUEST,
                    'NO_SUBJECT': status.HTTP_400_BAD_REQUEST,
                    'NO_CONTENT': status.HTTP_400_BAD_REQUEST,
                    'NO_EMAIL_SETTINGS': status.HTTP_400_BAD_REQUEST,
                    'MISSING_EMAIL_SETTINGS': status.HTTP_400_BAD_REQUEST,
                    'SMTP_AUTH_ERROR': status.HTTP_401_UNAUTHORIZED,
                    'SMTP_RECIPIENTS_REFUSED': status.HTTP_422_UNPROCESSABLE_ENTITY,
                    'SMTP_SERVER_DISCONNECTED': status.HTTP_503_SERVICE_UNAVAILABLE,
                    'SMTP_CONNECT_ERROR': status.HTTP_503_SERVICE_UNAVAILABLE,
                    'SMTP_TIMEOUT': status.HTTP_504_GATEWAY_TIMEOUT,
                    'UNEXPECTED_ERROR': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'SERVICE_ERROR': status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
                
                http_status = error_status_map.get(result.get('error'), status.HTTP_400_BAD_REQUEST)
                return Response(result, status=http_status)
        
        except Exception as e:
            logger.error(f"Unexpected error in SendEmailView: {str(e)}")
            return Response({
                'success': False,
                'error': 'INTERNAL_ERROR',
                'message': 'An internal server error occurred'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """Get email service information and health check"""
        return Response({
            'service': 'Email Service API',
            'version': '1.0.0',
            'status': 'active',
            'endpoints': {
                'send_email': {
                    'method': 'POST',
                    'description': 'Send email with attachments support',
                    'max_recipients': 100,
                    'max_attachments': 10,
                    'max_attachment_size': '25MB',
                    'max_total_attachment_size': '100MB'
                }
            }
        })






class ReceiveEmailView(APIView):
    def post(self, request):
        serializer = EmailReceiveSerializer(data=request.data)
        
        if serializer.is_valid():
            email_config = serializer.validated_data
            imap_config = {
                'host': email_config['host'],
                'username': email_config['username'],
                'password': email_config['password'],
                'port': email_config.get('port', 993),
                'use_ssl': email_config.get('use_ssl', True),
                'use_tls': email_config.get('use_tls', False),
                'protocol' : email_config.get('protocol', "IMAP"),
                'max_emails' : email_config.get('max_emails', max_emails),
                'folder' : email_config.get('folder', 'INBOX')
            }
            result = EmailReceiver.receive_emails(imap_config)
            if result['success']:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)