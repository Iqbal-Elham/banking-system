import datetime

from django import forms
from django.conf import settings
from accounts.models import User, UserAddress, UserBankAccount
from .models import Transaction


class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = [
            'amount',
            'transaction_type'
        ]

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)

        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()

    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()


class DepositForm(TransactionForm):

    def clean_amount(self):
        min_deposit_amount = settings.MINIMUM_DEPOSIT_AMOUNT
        amount = self.cleaned_data.get('amount')

        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f'You need to deposit at least {min_deposit_amount} AFN'
            )

        return amount


class WithdrawForm(TransactionForm):

    def clean_amount(self):
        account = self.account
        min_withdraw_amount = settings.MINIMUM_WITHDRAWAL_AMOUNT
        max_withdraw_amount = (
            account.account_type.maximum_withdrawal_amount
        )
        balance = account.balance

        amount = self.cleaned_data.get('amount')

        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at least {min_withdraw_amount} AFN'
            )

        if amount > max_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at most {max_withdraw_amount} AFN'
            )

        if amount > balance:
            raise forms.ValidationError(
                f'You have {balance} AFN in your account. '
                'You can not withdraw more than your account balance'
            )

        return amount


class TransactionDateRangeForm(forms.Form):
    daterange = forms.CharField(required=False)

    def clean_daterange(self):
        daterange = self.cleaned_data.get("daterange")

        try:
            daterange = daterange.split(' - ')
            if len(daterange) == 2:
                for date in daterange:
                    datetime.datetime.strptime(date, '%Y-%m-%d')
                return daterange
            else:
                raise forms.ValidationError("Please select a date range.")
        except (ValueError, AttributeError):
            raise forms.ValidationError("Invalid date range")

class TransferForm(forms.Form):
    recipient_account_number = forms.CharField(label='Recipient Account Number', widget=forms.TextInput(attrs={}))
    recipient_name = forms.CharField(label='Recipient Name', widget=forms.TextInput(attrs={'class': ''}))
    amount = forms.DecimalField(label='Amount', widget=forms.TextInput(attrs={'class': ''}))

    def clean_recipient_account_number(self):
        recipient_account_number = self.cleaned_data['recipient_account_number']
        if not UserBankAccount.objects.filter(account_no=recipient_account_number).exists():
            raise forms.ValidationError("This Account Number does not exist.")
        return recipient_account_number

    def clean_recipient_name(self):
        recipient_name = self.cleaned_data['recipient_name']
        if not User.objects.filter(first_name=recipient_name.title()).exists():
            raise forms.ValidationError("This Name does not exist.")
        return recipient_name

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount < 0:
            raise forms.ValidationError("The amount cannot be negative")
        return amount




class bootstrapStyleMixin:
    fields = None 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.fields:
            for fieldname in self.fields:
                self.fields[fieldname].widget.attrs = {
                    'class': 'inp w-100'
                    }
        
        else:
            raise ValueError('The field names must be set')


class UserEditForm(bootstrapStyleMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'profile_photo', 'email']

class UserAddressEditForm(bootstrapStyleMixin, forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = ['street_address', 'city', 'postal_code', 'country']

class UserAccountEditForm(bootstrapStyleMixin, forms.ModelForm):
    class Meta:
        model = UserBankAccount
        fields = ['birth_date', 'gender', 'phone_number']