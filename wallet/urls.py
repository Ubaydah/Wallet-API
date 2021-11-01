
from django.urls import path
from .views import *

urlpatterns = [
    path('user/', user_info, name="profile"),
    path('wallet_info/', WalletInfo.as_view()),
    path('wallet_info/transactions/', wallet_transactions),
    path('wallet_info/transactions/<int:transaction_pk>/', transaction_detail),
    path('register/', Register.as_view()),
    path('login/', Login.as_view()),
    path('deposit/', deposit_funds),
    path('transfer/', transfer_funds),
    path('deposit/verify/<str:reference>/', verify_deposit),
    path('create_recipient/', create_transfer_recipient),
    path('verify_account_number/', verify_account_number),
    path('withdraw/', withdraw_funds)

]
