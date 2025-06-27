from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Employees

@receiver(post_save, sender=Employees, dispatch_uid="send_welcome_mail_once")
def send_welcome_email_on_create(sender, instance, created, **kwargs):
    """
    Sends a welcome email once when a new employee is created.
    """
    if created and instance.user.email:
        try:
            print(f"Sending welcome email to {instance.user.email}")  # Debug log
            send_mail(
                subject="Welcome to the Company!",
                message=f"Hi {instance.user.first_name},\n\nWelcome aboard! We're excited to have you with us.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.user.email],
                fail_silently=False,
            )
            print("Welcome email sent successfully.")
        except Exception as e:
            print(f"Error sending welcome email: {e}")
    else:
        print("No email sent: either not created or user has no email.")


