
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
        from_email = 'your_email@gmail.com'  # Replace with your email
        recipient_list = [instance.account.user.email]  # User's email

        # send_mail(subject, message, from_email, recipient_list)

        if instance.transaction_type == TRANSFER:
            try:
                transfer = TransferMoney.objects.get(sender=instance.account)
                recipient_account = transfer.recipient

                subject = 'Transfer Notification'
                message = f'You have transferred ${instance.amount} to another account.'
                recipient_list = [instance.account.user.email]  # Sender's email

                send_mail(subject, message, from_email, recipient_list)

                receiver_subject = 'Received Money Notification'
                receiver_message = f'You have received ${instance.amount} in a transfer from {instance.account.user.username}.'
                receiver_recipient_list = [recipient_account.user.email]  # Receiver's email

                send_mail(receiver_subject, receiver_message, from_email, receiver_recipient_list)
            except TransferMoney.DoesNotExist:
                pass

        # if instance.transaction_type == RECEIVER:
        #     receiver_subject = 'Received Money'
        #     receiver_message = f'You have received ${instance.amount} in a transfer from {instance.sender.username}.'
        #     receiver_recipient_list = [instance.receiver.user.email]  # Receiver's email
        # elif instance.transaction_type == TRANSFER:
        #     subject = 'Received Money Notification'
        #     message = f'You have received ${instance.amount} from another account.'
        #     recipient_list = [instance.receiver.user.email]  # Receiver's email


        send_mail(receiver_subject, receiver_message, from_email, receiver_recipient_list)