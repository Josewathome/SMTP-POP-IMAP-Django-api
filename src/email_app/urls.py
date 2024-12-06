from django.urls import path
from .views import SendEmailView, ReceiveEmailView

urlpatterns = [
    path('send/', SendEmailView.as_view(), name='send_email'),
    path('receive/', ReceiveEmailView.as_view(), name='receive_email'),
]