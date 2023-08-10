from django.db import models
from .constants import TRANSACTION_TYPE_CHOICES
from accounts.models import UserBankAccount

class Transaction(models.Model):
    account = models.ForeignKey(
        UserBankAccount,
        related_name='transactions',
        on_delete=models.CASCADE,
    )
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=12
    )
    balance_after_transaction = models.DecimalField(
        decimal_places=2,
        max_digits=12
    )
    transaction_type = models.PositiveSmallIntegerField(
        choices=TRANSACTION_TYPE_CHOICES
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.account}'

    class Meta:
        ordering = ['timestamp']

class TransferMoney(models.Model):
    sender = models.ForeignKey(UserBankAccount, on_delete=models.CASCADE, related_name='sent_transactions')
    recipient = models.ForeignKey(UserBankAccount, on_delete=models.CASCADE, related_name='received_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'from ({self.sender}) - ({self.recipient})'