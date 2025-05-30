from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.db.models import Max
from django.core.exceptions import ValidationError

# Create your models here.
class Customer(AbstractUser):
    phone_number = models.CharField(max_length=10, unique=True)
    is_staff = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.phone_number}'

class Account(models.Model):
    account_owner = models.ForeignKey(Customer, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=10, unique=True, editable=False)
    account_amount = models.DecimalField(decimal_places=2, max_digits=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.account_owner.first_name}  {self.account_owner.last_name} - ({self.account_number})'

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.get_next_account_number()
        super().save(*args, **kwargs)

    @staticmethod
    def get_next_account_number():
        last_account = Account.objects.aggregate(max_account=Max('account_number'))['max_account']

        if last_account and last_account.isdigit():
            next_number = int(last_account) + 1
        else:
            next_number = 10000000

        return str(next_number).zfill(10)  # Always ensures 10 digits

class Transaction(models.Model):
    TRANSACTION_TYPES = (
    ('withdraw', 'Withdraw'),
    ('deposit', 'Deposit'),
    ('send', 'Send'),
    ('receive', 'Receive'),
    ('reverse', 'Reverse'),
    )
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.TextField(blank=True, null=True)
    reference_account = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reference_account',
        help_text='For Send/Receive transactions'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.transaction_type} - {self.amount} Account: {self.account.account_number}'

    class Meta:
        ordering = ('-timestamp',)

    def process_transaction(self):
        with transaction.atomic():
            # Lock rows
            account = Account.objects.select_for_update().get(id=self.account.id)

            if self.transaction_type == 'withdraw' or self.transaction_type == 'send':
                if account.account_amount < self.amount:
                    raise ValidationError("Insufficient funds")

                account.account_amount -= self.amount

            elif self.transaction_type == 'deposit' or self.transaction_type == 'receive':
                account.account_amount += self.amount

            else:
                raise ValidationError("Invalid transaction type")

            account.save()

            # Log transaction
            Transaction.objects.create(
                account=account,
                transaction_type=self.transaction_type,
                amount=self.amount,
                reference_account=self.reference_account,
                description=self.description
            )

            # If it's a send, log a "receive" for the recipient
            if self.transaction_type == 'send' and self.reference_account:
                receiver = Account.objects.select_for_update().get(id=self.reference_account.id)
                receiver.account_amount += self.amount
                receiver.save()

                Transaction.objects.create(
                    account=receiver,
                    transaction_type='receive',
                    amount=self.amount,
                    reference_account=account,
                    description=f"Received from: {account.account_owner}"
                )
