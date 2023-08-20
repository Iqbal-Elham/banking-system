from django.db import models

from django.contrib.auth.models import AbstractUser
# from django.core.validators import (
#     MinValueValidator,
#     MaxValueValidator,
# )
from .constants import GENDER_CHOICE
from .managers import UserManager


class User(AbstractUser):
    username = None
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True, default='img/default.png')
    email = models.EmailField(unique=True, null=False, blank=False)

    class Meta:
        swappable = 'AUTH_USER_MODEL'

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    @property
    def balance(self):
        if hasattr(self, 'account'):
            return self.account.balance
        return 0


class BankAccountType(models.Model):
    name = models.CharField(max_length=128)
    maximum_withdrawal_amount = models.DecimalField(
        decimal_places=2,
        max_digits=12
    )

    def __str__(self):
        return self.name


class UserBankAccount(models.Model):
    user = models.OneToOneField(
        User,
        related_name='account',
        on_delete=models.CASCADE,
    )
    account_type = models.ForeignKey(
        BankAccountType,
        related_name='accounts',
        on_delete=models.CASCADE
    )
    account_no = models.PositiveIntegerField(unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICE)
    birth_date = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    balance = models.DecimalField(
        default=0,
        max_digits=12,
        decimal_places=2
    )

    initial_deposit_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.email} - {self.account_no}'

class UserAddress(models.Model):
    user = models.OneToOneField(
        User,
        related_name='address',
        on_delete=models.CASCADE,
    )
    street_address = models.CharField(max_length=512)
    city = models.CharField(max_length=256)
    postal_code = models.PositiveIntegerField()
    country = models.CharField(max_length=256)

    def __str__(self):
        return self.user.email
