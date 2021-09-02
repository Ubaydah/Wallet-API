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


def is_amount(value):
    if value <= 0:
        raise serializers.ValidationError({"detail": "Invalid Amount"})
    return value

class DepositSerializer(serializers.Serializer):

    amount = serializers.IntegerField(validators=[is_amount])

    #def validate_amount(self, value):
        #if value <= 0:
            #raise serializers.ValidationError({"detail": "Invalid Amount"})
        #return value

    def save(self):
        print(self.context)
        user = self.context['request'].user
        wallet = Wallet.objects.get(user=user)
        data = self.validated_data
        print(self.validated_data)
        #users = CustomUser.objects.all()
        #print(users)
        deposit = WalletTransaction.objects.create(
            wallet = wallet,
            transaction_type = "deposit",
            amount = data["amount"],
            destination = wallet,
            status = "success",
        )
        return deposit


class TransferSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=100, decimal_places=2, validators=[is_amount])
    email = serializers.EmailField()

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            return value
        raise serializers.ValidationError({"detail": "Email not found"})
    
    def save(self):
        user = self.context['request'].user
        wallet = Wallet.objects.get(user=user)
        data = self.validated_data
        tuser = CustomUser.objects.get(email__exact=data["email"])
        transferWallet = Wallet.objects.get(user=tuser)

        balw = WalletTransaction.objects.filter(
            wallet=wallet).aggregate(Sum('amount'))['amount__sum']
        balt = WalletTransaction.objects.filter(
            wallet=transferWallet).aggregate(Sum('amount'))['amount__sum']
        
        
        
        if balw < data['amount']:
            raise serializers.ValidationError({"detail": "insufficient funds"})
        
        else:
            
        
            transfer = WalletTransaction.objects.create(
                wallet = wallet,
                transaction_type = "transfer",
                amount = data["amount"],
                source = wallet,
                destination = transferWallet,
                status = "success", 

            )
            balw = balw - data['amount']
            balt = balt + data['amount']
            return transfer
        
    



