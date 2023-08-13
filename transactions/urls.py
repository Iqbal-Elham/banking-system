from django.urls import path

from .views import DepositMoneyView, WithdrawMoneyView, TransactionRepostView, TransferMoneyView, UserProfileView


app_name = 'transactions'


urlpatterns = [
    path("deposit/", DepositMoneyView.as_view(), name="deposit_money"),
    path("transactions/", TransactionRepostView.as_view(), name="transaction_report"),
    path("withdraw/", WithdrawMoneyView.as_view(), name="withdraw_money"),
    path("transfer/", TransferMoneyView, name="transfer_money"),
    path("profile/", UserProfileView, name="user_profile"),
]
