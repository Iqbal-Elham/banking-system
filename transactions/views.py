from dateutil.relativedelta import relativedelta
from django.http import HttpResponse

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView

from transactions.constants import DEPOSIT, WITHDRAWAL, TRANSFER, RECEIVER
from transactions.forms import (
    DepositForm,
    TransactionDateRangeForm,
    WithdrawForm,
)
from django.contrib.auth.decorators import login_required
from transactions.models import Transaction, TransferMoney
from accounts.models import UserBankAccount
from .forms import TransferForm

from accounts.models import User

from django.core.mail import send_mail
from django.core.signals import request_finished
from django.db.models.signals import post_save
from django.dispatch import receiver
from .signals import send_transaction_email

class TransactionRepostView(LoginRequiredMixin, ListView):
    template_name = 'transactions/transactions_report.html'
    model = Transaction
    form_data = {}

    def get(self, request, *args, **kwargs):
        form = TransactionDateRangeForm(request.GET or None)
        if form.is_valid():
            self.form_data = form.cleaned_data

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account=self.request.user.account
        )

        daterange = self.form_data.get("daterange")

        if daterange:
            queryset = queryset.filter(timestamp__date__range=daterange)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account,
            'form': TransactionDateRangeForm(self.request.GET or None)
        })

        return context


class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transactions_form.html'
    model = Transaction
    title = ''
    success_url = reverse_lazy('transactions:transaction_report')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title
        })

        return context


class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = 'Deposit Money to Your Account'

    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account

        if not account.initial_deposit_date:
            now = timezone.now()


        account.balance += amount
        account.save(
            update_fields=[
                'initial_deposit_date',
                'balance',
            ]
        )

        messages.success(
            self.request,
            f'{amount}$ was deposited to your account successfully'
        )

        return super().form_valid(form)


class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Withdraw Money from Your Account'

    def get_initial(self):
        initial = {'transaction_type': WITHDRAWAL}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')

        self.request.user.account.balance -= form.cleaned_data.get('amount')
        self.request.user.account.save(update_fields=['balance'])


        messages.success(
            self.request,
            f'Successfully withdrawn {amount}$ from your account'
        )

        return super().form_valid(form)
    
@login_required
def TransferMoneyView(request):

    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            recipient_account_number = form.cleaned_data['recipient_account_number']
            recipient_name = form.cleaned_data['recipient_name']
            amount = form.cleaned_data['amount']

            try:
                sender_account = UserBankAccount.objects.get(user=request.user)
                recipient_account = UserBankAccount.objects.get(account_no=recipient_account_number)
            except UserBankAccount.DoesNotExist:
                return HttpResponse("Account not found.")

            if sender_account.balance >= amount:
                sender_account.balance -= amount
                recipient_account.balance += amount

                Transaction.objects.create(
                    account=sender_account,
                    amount=amount,
                    balance_after_transaction=sender_account.balance, 
                    transaction_type=TRANSFER
                    )

                Transaction.objects.create(
                    account=recipient_account,
                    amount=amount,
                    balance_after_transaction=recipient_account.balance, 
                    transaction_type=RECEIVER
                    )

                sender_account.save()
                recipient_account.save()
                
                 # Send email to sender
                sender_subject = 'Transfer Notification'
                sender_message = f'You have transferred ${amount} to {recipient_name}\'s account.'
                sender_recipient_list = [request.user.email]  # Sender's email

                send_mail(sender_subject, sender_message, 'iqbal.ilhamm.77@gmail.com', sender_recipient_list)

                # Send email to recipient
                recipient_subject = 'Received Money Notification'
                recipient_message = f'You have received ${amount} in a transfer from {request.user.username}.'
                recipient_recipient_list = [recipient_account.user.email]  # Receiver's email

                send_mail(recipient_subject, recipient_message, 'iqbal.ilham.77@gmail.com', recipient_recipient_list)

                TransferMoney.objects.create(sender=sender_account, recipient=recipient_account, amount=amount)

                messages.success(
                    request,
                    f'Successfully transferred {amount}$ to {recipient_name}\'s account'
                )

                return redirect('transactions:transaction_report')
    else:
        form = TransferForm()

    return render(request, 'transactions/transfer.html', {'form': form})


def UserProfileView(request):
    user_id = request.user.id
    user = User.objects.get(id=user_id)  # Fetch the user's data

    context = {
        'user': user,  # Pass the user object to the template context
    }

    # user_id = request.user.id
    # user = User.objects.get(id=user_id)
    # books = Book.objects.filter(user=user)
    # profile = user_profile.objects.filter(user=request.user).first()
    # editForm = editRegisterForm(request.POST or None, request.FILES or None,
    # initial={
    #     'user_name':user.username, 
    #     'email':user.email,
    #     'profile_pic':profile.profile_pic,
    #     'city':profile.city,
    #     'address':profile.address,
    #     'gender':profile.gender,
    #     'phone_num':profile.phone_num,
    #     'whatsapp_num':profile.whatsapp_num,
    #     })
    # if editForm.is_valid():
    #     profile_pic = editForm.cleaned_data.get('profile_pic')
    #     user_name = editForm.cleaned_data.get('user_name')
    #     email = editForm.cleaned_data.get('email')
    #     city = editForm.cleaned_data.get('city')
    #     address = editForm.cleaned_data.get('address')
    #     gender = editForm.cleaned_data.get('gender')
    #     phone_num = editForm.cleaned_data.get('phone_num')
    #     whatsapp_num = editForm.cleaned_data.get('whatsapp_num')
    #     username_is_exist = User.objects.filter(username=user_name).exists()
    #     email_is_exist = User.objects.filter(email=email).exists()
    #     if username_is_exist:
    #         if user.username == user_name:
    #             pass
    #         else:
    #             messages.error(request, "The username already exists")   
    #     else:
    #         user.username = user_name

    #     if email_is_exist:
    #         if user.email == email:
    #             pass
    #         else:
    #             messages.warning(request, "The email already exists")   
    #     else:
    #         user.email = email

    #     user.user_profile.city = city
    #     user.user_profile.address = address
    #     user.user_profile.gender = gender
    #     user.user_profile.phone_num = phone_num
    #     user.user_profile.whatsapp_num = whatsapp_num
    #     user.user_profile.profile_pic = profile_pic
    #     user.save()
    #     user.user_profile.save()
        
    # context = {
    #         'editForm' : editForm,
    #         'books' : books,
    #     }
    
    return render(request, 'transactions/user_profile.html', context)

