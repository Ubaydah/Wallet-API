import json
from django.http.response import JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate
from requests import api
from rest_framework.decorators import api_view
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .serializers import *
from .models import *
from rest_framework import generics
from rest_framework import status
from django.utils import timezone
import requests
from django.conf import settings
# Create your views here


class Login(APIView):
    permission_classes = ()

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(email=email, password=password)
        if user:
            return Response({"token": user.auth_token.key, "email": email})
        else:
            return Response({"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)


class Register(generics.CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer


@api_view(["GET"])
def user_info(request):
    print(request.headers)
    user = request.user
    data = UserSerializer(user).data
    return Response(data)


class WalletInfo(APIView):
    def get(self, request):
        wallet = Wallet.objects.get(user=request.user)
        data = WalletSerializer(wallet).data
        return Response(data)


@api_view(['GET'])
def wallet_transactions(request):
    #paginator = PageNumberPagination()
    #wallet = Wallet.objects.get(user=request.user)
    transactions = WalletTransaction.objects.filter(wallet__user=request.user)
    #context = paginator.paginate_queryset(transactions, request)
    serializer = WalletTransactionSerializer(transactions, many=True)

    return Response(serializer.data)


@api_view(['GET'])
def transaction_detail(request, transaction_pk):
    try:
        transaction = WalletTransaction.objects.get(
            id=transaction_pk, wallet__user=request.user)
    except WalletTransaction.DoesNotExist:
        return Response({"status": False, "detail": "Transaction Not Found"}, status.HTTP_404_NOT_FOUND)

    serializer = WalletTransactionSerializer(transaction)

    return Response(serializer.data)


@api_view(['POST'])
def deposit_funds(request):
    serializer = DepositSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    
    deposit = serializer.save()


    return Response(deposit)

"""
    Used to verify the deposit done 

"""

@api_view(['GET'])
def verify_deposit(request, reference): 
    transaction = WalletTransaction.objects.get(paystack_payment_reference=reference, wallet__user=request.user)
    reference = transaction.paystack_payment_reference
    url = 'https://api.paystack.co/transaction/verify/{}'.format(reference)
    headers = {"Authorization": "Bearer sk_test_30ce4bbbb67824917f4893d27f7ad8b170ea02bd"}
    r = requests.get(url, headers=headers)
    resp = r.json()
    if resp['data']['status'] == 'success':
        status = resp['data']['status']
        amount = resp['data']['amount']
        WalletTransaction.objects.filter(paystack_payment_reference=reference).update(status=status, 
        amount=amount)
        return Response(resp)
    return Response(resp)


@api_view(['POST'])
def verify_account_number(request):
    serializer = VerifyAccountSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    response = serializer.save()

    return Response(response)
 
@api_view(['POST'])
def create_transfer_recipient(request):
    serializer = TransferRecipientSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    recipient = serializer.save()
    return Response(recipient)

@api_view(['POST'])
def withdraw_funds(request):
    serializer = WithdrawalSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    response = serializer.save()

    return Response(response)


@api_view(['POST'])
def transfer_funds(request):
    serializer = TransferSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    response = serializer.save()
    return Response(response)




 
