
from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from django.core.validators import RegexValidator

from .models import User, BankAccountType, UserBankAccount, UserAddress
from .constants import GENDER_CHOICE

from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm


class Capitalize(forms.CharField):
    def to_python(self, value):
        return value.title()

class UserAddressForm(forms.ModelForm):

    class Meta:
        model = UserAddress
        fields = [
            'street_address',
            'city',
            'postal_code',
            'country'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'form-control'
                ),
                'placeholder': self.fields[field].label
            })


class UserRegistrationForm(UserCreationForm):
    account_type = forms.ModelChoiceField(
        queryset=BankAccountType.objects.all()
    )
    gender = forms.ChoiceField(choices=GENDER_CHOICE)
    birth_date = forms.DateField()
    phone_number = forms.CharField(max_length=20, label="e.g +93 XXXXXXXXX", widget=forms.TextInput(
         attrs={
                'data-mask': '(+00) 000-000-0000'
                }
    ))


    first_name = Capitalize(
        max_length=100,
        validators=[
                RegexValidator(r'^[a-zA-ZÀ-ÿ\s]*$', message='Only letters are allowed'),
                ],
        widget=forms.TextInput(attrs={'placeholder': 'Firstname'}),
        label="First name",
    )
    last_name = Capitalize(
        max_length=100,
        validators=[
                RegexValidator(r'^[a-zA-ZÀ-ÿ\s]*$', message='Only letters are allowed'),
                ],
        widget=forms.TextInput(attrs={'placeholder': 'Lastname'}),
        label="Last name"
    )

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'profile_photo',
            'email',
            'password1',
            'password2',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'form-control'
                ),
                'placeholder': self.fields[field].label
            })

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            account_type = self.cleaned_data.get('account_type')
            gender = self.cleaned_data.get('gender')
            phone_number = self.cleaned_data.get('phone_number')
            birth_date = self.cleaned_data.get('birth_date')

            UserBankAccount.objects.create(
                user=user,
                gender=gender,
                birth_date=birth_date,
                account_type=account_type,
                phone_number=phone_number,
                account_no=(
                    user.id +
                    settings.ACCOUNT_NUMBER_START_FROM
                )
            )
        return user
    


class bootstrapStyleMixin:
    field_names = None 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.field_names:
            for fieldname in self.field_names:
                self.fields[fieldname].widget.attrs = {
                    'class': 'form-control mt-1', 
                    'placeholder': f'Enter {fieldname}'
                    }
        
        else:
            raise ValueError('The field names must be set')


class MyResetPassForm(bootstrapStyleMixin, PasswordResetForm):
    field_names = ['email']
    
class MySetPassForm(bootstrapStyleMixin, SetPasswordForm):
    field_names = ['new_password1', 'new_password2']


class MyPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for fieldname in ['old_password', 'new_password1', 'new_password2']:
            self.fields[fieldname].widget.attrs = {'class': 'inp d-block'}
