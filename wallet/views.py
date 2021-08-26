from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .serializers import WalletSerializer, WalletTransactionSerializer, UserSerializer
from .models import *
from rest_framework import generics
from rest_framework import status
from django.db.models import Sum
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

  
class UserInfo(APIView):
    def get(self, request, pk):
        user = CustomUser.objects.get(pk=pk)
        data = UserSerializer(user).data

        return Response(data)

class WalletInfo(APIView):
    def get(self, request, pk):
        wallet = Wallet.objects.get(pk=pk)
        data = WalletSerializer(wallet).data

        return Response(data)

@api_view(['GET'])
def wallet_transactions(request, pk):
    #paginator = PageNumberPagination()
    wallet = Wallet.objects.get(id=pk)
    transactions = WalletTransaction.objects.filter(wallet=wallet)
    #context = paginator.paginate_queryset(transactions, request)
    serializer = WalletTransactionSerializer(transactions, many=True)

    return Response(serializer.data)

@api_view(['GET'])
def transaction_detail(request, pk, transaction_pk):
    transaction = WalletTransaction.objects.get(id=transaction_pk)

    serializer = WalletTransactionSerializer(transaction)

    return Response(serializer.data)


@api_view(['POST'])
def deposit_funds(self, request):
    serializer = WalletSerializer(data=request.data['amount'])
    if serializer.is_valid():
        #serializer.data['balance'] += request.data
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET', 'POST'])
def transfer(request):
    pass
