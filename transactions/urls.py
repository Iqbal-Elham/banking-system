from django.urls import path

from .views import (
    DepositMoneyView, 
    WithdrawMoneyView, 
    TransactionRepostView, 
    TransferMoneyView, 
    UserProfileView, 
    print_transactions_pdf,
    EditUserProfileView,
    currency_exchange,
)

app_name = 'transactions'


urlpatterns = [
    path("deposit/", DepositMoneyView.as_view(), name="deposit_money"),
    path("transactions/", TransactionRepostView.as_view(), name="transaction_report"),
    path("withdraw/", WithdrawMoneyView.as_view(), name="withdraw_money"),
    path("transfer/", TransferMoneyView, name="transfer_money"),
    path("profile/", UserProfileView, name="user_profile"),
    path('print_transactions/', print_transactions_pdf, name='print_transactions'),
    path('edit-profile/', EditUserProfileView.as_view(), name='edit_profile'),
    path("currency-exchange/", currency_exchange, name="currency_exchange"),
    
]
