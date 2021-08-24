from .models import Wallet, WalletTransaction, CustomUser
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.db.models import Sum


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'password']
        extra_kwargs = {'password':{'write_only': True}}

    def create(self, validated_data):
        user = CustomUser(
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        Token.objects.create(user=user)
        return user

class WalletSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()

    def get_balance(self, obj):
        bal = WalletTransaction.objects.filter(wallet=obj).aggregate(Sum('amount'))
        return bal

    class Meta:
        model = Wallet
        fields = ['id', 'currency', 'balance']

class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = ['id', 'transaction', 'amount', 'source', 'destination',]