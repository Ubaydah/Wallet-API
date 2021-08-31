from .models import Wallet, WalletTransaction, CustomUser
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.db.models import Sum


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

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
        bal = WalletTransaction.objects.filter(
            wallet=obj).aggregate(Sum('amount'))['amount__sum']
        return bal

    class Meta:
        model = Wallet
        fields = ['id', 'currency', 'balance']


class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = ['id', 'transaction_type', 'amount', 'source', 'destination', ]


class DepositSerializer(serializers.Serializer):

    amount = serializers.IntegerField()

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError({"detail": "Invalid Amount"})
        return value

    def save(self):
        print(self.context)
        user = self.context['request'].user
        wallet = Wallet.objects.get(user=user)
        data = self.validated_data
        print(self.validated_data)
        deposit = WalletTransaction.objects.create(
            wallet = wallet,
            transaction_type = "deposit",
            amount = data["amount"],
            destination = wallet,
            status = "success",
        )
        return deposit


