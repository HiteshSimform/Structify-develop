from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Employees


def _build_welcome_email(employee: Employees) -> EmailMultiAlternatives:
    """
    Prepare the subject, plain-text, and HTML versions of the welcome e-mail.
    """
    user = employee.user
    context = {
        "first_name": user.first_name or user.username,
        "department": employee.department.name if employee.department else "your team",
        "hire_date": employee.hire_date,
        "company_name": settings.COMPANY_NAME,          
        "portal_url": settings.FRONTEND_URL,            
    }

    subject = render_to_string(
        "emails/welcome_employee_subject.txt", context
    ).strip()

    text_body = render_to_string(
        "emails/welcome_employee.txt", context
    )
    html_body = render_to_string(
        "emails/welcome_employee.html", context
    )

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    message.attach_alternative(html_body, "text/html")
    return message


@receiver(post_save, sender=Employees, dispatch_uid="send_welcome_mail_once")
def send_welcome_email_on_create(sender, instance: Employees, created, **kwargs):
    """
    Fires **one time** after an Employees row is inserted.
    """
    if not created:
        return

    if not instance.user.email:
        return
