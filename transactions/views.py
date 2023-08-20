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
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,  Spacer

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

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

                current_datetime = timezone.now()
                
                 # Send email to sender
                sender_subject = 'Transfer Notification'
                sender_message = f'You have transferred {amount} AFN to {recipient_name}\'s account with the Account Number: {recipient_account.account_no}'
                sender_recipient_list = [request.user.email]  # Sender's email
                sender_name = request.user.first_name

                template_name = "emails/transfer.html"
                context = {"message": sender_message, 'subject': sender_subject, 'current_datetime':current_datetime}

                sender_email_body = render_to_string(template_name, context)

                email = EmailMessage(
                        sender_subject,
                        sender_email_body,
                        settings.DEFAULT_FROM_EMAIL,  # Sender's email
                        sender_recipient_list,  # List of recipient email addresses
                    )
                
                email.content_subtype = "html"

                email.send()

                # Send email to recipient
                recipient_subject = 'Received Money Notification'
                recipient_message = f'You have received {amount} AFN in a transfer from {request.user.first_name} with the Account number: {request.user.account.account_no}.'
                recipient_recipient_list = [recipient_account.user.email]  # Receiver's email
                recipient_name = request.user.first_name

                template_name = "emails/receive.html"
                context = {"message": recipient_message, 'subject': recipient_subject, 'amount': amount, 'current_datetime': current_datetime}

                email_body = render_to_string(template_name, context)

                email = EmailMessage(
                        recipient_subject,
                        email_body,
                        settings.DEFAULT_FROM_EMAIL,  # Sender's email
                        recipient_recipient_list,  # List of recipient email addresses
                    )
                
                email.content_subtype = "html"

                email.send()
                

                TransferMoney.objects.create(sender=sender_account, recipient=recipient_account, amount=amount)

                messages.success(
                    request,
                    f'Successfully transferred {amount}$ to {recipient_name}\'s account'
                )

                return redirect('transactions:transaction_report')
    else:
        form = TransferForm()

    return render(request, 'transactions/transfer.html', {'form': form})

@login_required
def print_transactions_pdf(request):
    user = request.user.id
    transactions = Transaction.objects.filter(account_id=user) 

    # form = TransactionDateRangeForm(request.POST)
    # print(form)
    # if form.is_valid():
    #     start_date, end_date = form.cleaned_data['daterange']
    #     print("helllooo",  start_date, end_date)
    #     transactions = Transaction.objects.filter(account_id=user, timestamp__range=(start_date, end_date))
    # else:
    #     transactions = Transaction.objects.filter(account_id=user)
    #     print("jjjjjjj", transactions)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="transactions.pdf"'

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    try:
        user_account = User.objects.get(id=user)
        print(user_account)
        account_details = [
            ['Full name:', user_account.get_full_name()],
            ['Email:', user_account.email],
            ['User Account Number:', user_account.account.account_no],
            ['Bank:', 'Banker, The first digital banking system'],
        ]
    except UserBankAccount.DoesNotExist:
        account_details = []

    details_table = Table(account_details)
    details_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(details_table)

    elements.append(Spacer(1, 30))

    # Create a list of lists containing transaction data for the table
    data = [['transaction type', 'date', 'Amount', 'Balance After Transaction']]
    for transaction in transactions:
        balance = transaction.balance_after_transaction
        if transaction.transaction_type == 1:
            transaction.transaction_type = 'Deposit'
        elif transaction.transaction_type == 2:
            transaction.transaction_type = 'Withdrawal'
        elif transaction.transaction_type == 3:
            transaction.transaction_type = 'Transfer'
        elif transaction.transaction_type == 4:
            transaction.transaction_type = 'Received'
        data.append([transaction.transaction_type, 
                     transaction.timestamp.strftime('%Y-%m-%d %H:%M'), 
                     transaction.amount, 
                     transaction.balance_after_transaction,])
    data.append(['', '','Total Balance', balance])

    # Create the table and set its style
    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), 'purple'),
        ('TEXTCOLOR', (0, 0), (-1, 0), (1, 1, 1)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), (0.9, 0.9, 0.9)),
        ('GRID', (0, 0), (-1, -1), 1, (0.7, 0.7, 0.7)),
    ])
    table.setStyle(style)

    elements.append(table)
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response

@login_required
def UserProfileView(request):
    user_id = request.user.id
    user = User.objects.get(id=user_id) 

    context = {
        'user': user, 
    }

    return render(request, 'transactions/user_profile.html', context)

# def edit_profile(request):
#     user_profile = UserProfile.objects.get(user=request.user)
    
#     if request.method == 'POST':
#         form = UserProfileForm(request.POST, instance=user_profile)
#         if form.is_valid():
#             form.save()
#             return redirect('profile')  # Redirect to the user's profile page
#     else:
#         form = UserProfileForm(instance=user_profile)
    
#     context = {'form': form}
#     return render(request, 'edit_profile.html', context)

