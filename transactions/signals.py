
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Transaction, TransferMoney
from .constants import DEPOSIT, WITHDRAWAL

from django.utils import timezone
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings



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
                message = f'You have deposited {instance.amount} AFN to your account.'
                recipient_list = [instance.account.user.email] 
                recipient_name = instance.account.user.first_name
                current_datetime = timezone.now()

                template_name = "emails/deposit.html"
                context = {"recipient_name": recipient_name, 'message':message, 'current_datetime':current_datetime}

                email_body = render_to_string(template_name, context)

                email = EmailMessage(
                        subject,
                        email_body,
                        settings.DEFAULT_FROM_EMAIL,  
                        recipient_list, 
                    )
                
                email.content_subtype = "html"

                email.send()

            except TransferMoney.DoesNotExist:
                pass
        elif instance.transaction_type == WITHDRAWAL:
            try:
                subject = 'Your Money Withdraw Successfully'
                message = f'You have withdrawn {instance.amount} AFN from your account.'
                recipient_list = [instance.account.user.email]
                recipient_name = instance.account.user.first_name
                current_datetime = timezone.now()

                template_name = "emails/withdraw.html"
                context = {"message": message, 'subject': subject, 'current_datetime': current_datetime}

                email_body = render_to_string(template_name, context)

                email = EmailMessage(
                        subject,
                        email_body,
                        settings.DEFAULT_FROM_EMAIL, 
                        recipient_list, 
                    )
                
                email.content_subtype = "html"

                email.send()

            except TransferMoney.DoesNotExist:
                pass
    