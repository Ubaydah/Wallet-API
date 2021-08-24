
from django.urls import path
from .views import UserInfo, WalletInfo, wallet_transactions, transaction_detail, Register, Login, deposit_funds, transfer

urlpatterns = [
    path('user_info/<int:pk>/', UserInfo.as_view()),
    path('wallet_info/<int:pk>/', WalletInfo.as_view()),
    path('wallet_info/<int:pk>/transactions/', wallet_transactions),
    path('wallet_info/<int:pk>/transactions/<int:transaction_pk>/', transaction_detail),
    path('register/', Register.as_view()),
    path('login/', Login.as_view()),
    path('deposit/', deposit_funds),
    path('transfer/',transfer),

]