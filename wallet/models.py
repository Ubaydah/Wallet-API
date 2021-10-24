from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from .managers import CustomUserManager
from django.conf import settings
from django.utils import timezone

# Create your models here.


class CustomUser(AbstractUser):

    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    currency = models.CharField(max_length=50, default='NGN')
    created_at = models.DateTimeField(default=timezone.now, null=True)

    def __str__(self):
        return self.user.__str__()


class WalletTransaction(models.Model):

    TRANSACTION_TYPES = (
        ('deposit', 'deposit'),
        ('transfer', 'transfer'),
    )
    wallet = models.ForeignKey(Wallet, null=True, on_delete=models.CASCADE)
    transaction_type = models.CharField(
        max_length=200, null=True,  choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=100, null=True, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now, null=True)
    source = models.ForeignKey(
        Wallet, null=True, on_delete=models.CASCADE, related_name='source', blank=True)
    destination = models.ForeignKey(
        Wallet, null=True, on_delete=models.CASCADE, related_name='destination', blank=True)
    status = models.CharField(max_length=100, default="pending")
    paystack_payment_reference = models.CharField(max_length=100, default='', blank=True)

    def __str__(self):
        return self.wallet.user.__str__()
