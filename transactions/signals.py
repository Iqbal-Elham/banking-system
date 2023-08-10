
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Transaction, TransferMoney
from .constants import DEPOSIT, WITHDRAWAL, TRANSFER, RECEIVER

@receiver(post_save, sender=Transaction)
def send_transaction_email(sender, instance, created, **kwargs):
    if created:
        subject = 'Transaction Notification'
        message = f'You have performed a {instance.get_transaction_type_display()} transaction of ${instance.amount}.'
        from_email = 'iqbal.ilham.77@gmail.com'
        recipient_list = [instance.account.user.email]

        if instance.transaction_type == DEPOSIT:
            try:
                subject = 'Your Money Deposit Successfully'
                message = f'You have deposited ${instance.amount} to your account.'
                recipient_list = [instance.account.user.email]  # Receiver's email

                send_mail(subject, message, from_email, recipient_list)
            except TransferMoney.DoesNotExist:
                pass
        elif instance.transaction_type == WITHDRAWAL:
            try:
                subject = 'Your Money Withdraw Successfully'
                message = f'You have withdrawn ${instance.amount} from your account.'
                recipient_list = [instance.account.user.email]

                send_mail(subject, message, from_email, recipient_list)
            except TransferMoney.DoesNotExist:
                pass