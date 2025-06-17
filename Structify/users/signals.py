from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser
from leaves.utils import allocate_leave_balances


@receiver(post_save, sender=CustomUser)
def create_leave_balances(sender, instance, created, **kwargs):
    if created and instance.role == "EMPLOYEE":  # adjust role check if needed
        allocate_leave_balances(employee=instance, created_by=instance)
