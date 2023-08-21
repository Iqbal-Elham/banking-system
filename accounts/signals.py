from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User  # Import your User model

@receiver(pre_save, sender=User)
def capitalize_first_name(sender, instance, **kwargs):
    instance.first_name = instance.first_name.capitalize()
