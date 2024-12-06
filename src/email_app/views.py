from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import EmailSerializer, EmailReceiveSerializer
from .service import EmailReceiver ,EmailService, max_emails
class SendEmailView(APIView):
    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        
        if serializer.is_valid():
            email_data = serializer.validated_data
            result = EmailService.send_email(
                email_settings=email_data.get('email_settings', {}),
                sender=email_data['sender'],
                recipients=email_data['recipients'],
                subject=email_data['subject'],
                body=email_data['body'],
                cc=email_data.get('cc', []),
                bcc=email_data.get('bcc', []),
                attachments=email_data.get('attachments', []),
                use_default_settings=email_data.get('use_default_settings', False)
            )
            if result['success']:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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