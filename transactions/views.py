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


                sender_account.save(update_fields=['balance'])
                recipient_account.save(update_fields=['balance'])

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

