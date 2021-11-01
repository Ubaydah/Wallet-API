from .models import Wallet, WalletTransaction, CustomUser
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.db.models import Sum
import requests 


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
    email = serializers.EmailField()
    #def validate_amount(self, value):
        #if value <= 0:
            #raise serializers.ValidationError({"detail": "Invalid Amount"})
        #return value
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            return value
        raise serializers.ValidationError({"detail": "Email not found"})


    def save(self):
        user = self.context['request'].user
        wallet = Wallet.objects.get(user=user)
        data = self.validated_data
        url = 'https://api.paystack.co/transaction/initialize'
        headers = {"Authorization": "Bearer sk_test_30ce4bbbb67824917f4893d27f7ad8b170ea02bd"}
        r = requests.post(url, headers=headers, data=data)
        response = r.json()
        deposit = WalletTransaction.objects.create(
            wallet = wallet,
            transaction_type = "deposit",
            amount = 0, #data["amount"],
            paystack_payment_reference = response['data']['reference'],
            destination = wallet,
            status = "pending",
        )

        return response

class VerifyAccountSerializer(serializers.Serializer):
    account_number = serializers.CharField(max_length=100)
    bank_code = serializers.CharField(max_length=100)


    def save(self):
        user = self.context['request'].user
        data = self.validated_data
        account_number = data['account_number']
        bank_code = data['bank_code']
        url = 'https://api.paystack.co/bank/resolve?account_number={}&bank_code={}'.format(account_number, bank_code)
        headers = {"Authorization": "Bearer sk_test_30ce4bbbb67824917f4893d27f7ad8b170ea02bd"}
        r = requests.get(url, headers=headers)
        resp = r.json()
        if resp['message'] == "Account number resolved":
            Wallet.objects.filter(user=user).update(account_number=account_number, bank_code=bank_code)

            return resp
        return resp


class TransferRecipientSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=250)

    
    def save(self):
        user = self.context['request'].user
        data = self.validated_data
        name = data['name']
        wallet = Wallet.objects.get(user=user)
        account_number = wallet.account_number
        bank_code = wallet.bank_code
        url = 'https://api.paystack.co/transferrecipient'
        headers = {"Authorization": "Bearer sk_test_30ce4bbbb67824917f4893d27f7ad8b170ea02bd"}
        data = { "type": "nuban",
            "name": name,
            "account_number": account_number,
            "bank_code": bank_code,
            "currency": "NGN"
        }
        r = requests.post(url, headers=headers, data=data)
        resp = r.json()
        recipient_code = resp['data']['recipient_code']
        Wallet.objects.filter(user=user).update(recipient_code=recipient_code)

        return resp

def get_balance(wallet):

        bal = WalletTransaction.objects.filter(
            wallet=wallet).aggregate(Sum('amount'))['amount__sum']
        
        return bal

class WithdrawalSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=100, decimal_places=0, validators=[is_amount])

    def save(self):
        user = self.context['request'].user
        wallet = Wallet.objects.get(user=user)
        data = self.validated_data
        amount = data['amount']

        bal_wallet = get_balance(wallet)

        if bal_wallet < data['amount']:
            raise serializers.ValidationError({"detail": "insufficient funds"})
        
        else:

            url = 'https://api.paystack.co/transfer'
            headers = {"Authorization": "Bearer sk_test_30ce4bbbb67824917f4893d27f7ad8b170ea02bd"}
            recipient_code = wallet.recipient_code
            data = {
                "source": "balance",
                "amount": amount,
                "recipient": recipient_code
            }
            r = requests.post(url, headers=headers, data=data)
            resp = r.json()

            if resp['message'] == 'Transfer has been queued':
                transfer_code = resp["data"]["transfer_code"]
                WalletTransaction.objects.create(
                wallet = wallet,
                transaction_type = "withdraw",
                amount = -amount,
                source = wallet, 
                status = "success",
                paystack_payment_reference = transfer_code 

            )

                return resp
            else:
                return resp
        
        


class TransferSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=100, decimal_places=0, validators=[is_amount])
    destination = serializers.IntegerField()

    def validate_destination(self, value):
        if CustomUser.objects.filter(id=value).exists():
            return value
        raise serializers.ValidationError({"detail": "Id not found"})

    """
    def get_balance(self, wallet):

        bal = WalletTransaction.objects.filter(
            wallet=wallet).aggregate(Sum('amount'))['amount__sum']
        
        return bal
    """
    def save(self):
        user = self.context['request'].user
        wallet = Wallet.objects.get(user=user)
        data = self.validated_data
        amount = data['amount']
        transfer_user = CustomUser.objects.get(id__exact=data["destination"])
        transferWallet = Wallet.objects.get(user=transfer_user)

       
        bal_wallet = get_balance(wallet)

        if bal_wallet < data['amount']:
            raise serializers.ValidationError({"detail": "insufficient funds"})
        
        else:
            
            url = 'https://api.paystack.co/transfer'
            headers = {"Authorization": "Bearer sk_test_30ce4bbbb67824917f4893d27f7ad8b170ea02bd"}
            recipient_code = transferWallet.recipient_code
            data = {
                "source": "balance",
                "amount": amount,
                "recipient": recipient_code
            }
            r = requests.post(url, headers=headers, data=data)
            resp = r.json()

            if resp['message'] == 'Transfer has been queued':
                transfer_code = resp["data"]["transfer_code"]
                
                WalletTransaction.objects.create(
                wallet = wallet,
                transaction_type = "transfer",
                amount = -amount,
                source = wallet, 
                destination = transferWallet,
                status = "success", 

            )

               
                WalletTransaction.objects.create(
                wallet = transferWallet,
                transaction_type = "transfer", 
                amount = amount,
                source = wallet,
                destination = transferWallet,
                status = "success",
                paystack_payment_reference = transfer_code, 

            )

                return resp
            else:
                return resp           
        

            
        
    



