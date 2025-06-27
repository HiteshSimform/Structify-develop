from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LeaveApplication
from django.core.mail import send_mail


@receiver(post_save, sender=LeaveApplication)
def notify_leave_status_change(sender, instance, created, **kwargs):
    if not created and instance.status in ["Approved", "Rejected"]:
        subject = f"Leave {instance.status}: {instance.leave_type.name}"
        message = f"""
        Hi {instance.employee.user.name},

        Your leave from {instance.start_date} to {instance.end_date} has been {instance.status.lower()}.
        Reason: {instance.reason}

        Thank you.
        """
        to_email = instance.employee.user.email
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email])
