from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Transaction


@receiver(post_save, sender=Transaction)
def send_transaction_email(sender, instance, created, **kwargs):
    if created:
        subject = 'Transaction Notification'
        message = f'You have performed a transaction of ${instance.amount}.'
        from_email = 'your_email@gmail.com'
        recipient_list = [instance.user.email]  # User's email

        send_mail(subject, message, from_email, recipient_list)

        if instance.receiver:
            receiver_subject = 'Received Money'
            receiver_message = f'You have received ${instance.amount} from {instance.user.username}.'
            receiver_recipient_list = [instance.receiver.email]  # Receiver's email

            send_mail(receiver_subject, receiver_message, from_email, receiver_recipient_list)