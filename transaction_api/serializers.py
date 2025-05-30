from django.contrib.auth.models import User
from rest_framework import serializers
from transaction_api.models import Customer, Account, Transaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # Hashes the password
        user.save()
        return user

class AccountSerializer(serializers.ModelSerializer):
    # For writing: accept a Customer's ID
    account_owner = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    # For reading: provide detailed info about the Customer
    account_owner_details = CustomerSerializer(source='account_owner', read_only=True)
    class Meta:
        model = Account
        fields = ['id', 'account_number', 'account_owner','account_amount', 'account_owner_details']

class TransactionSerializer(serializers.ModelSerializer):
    # for writing: acept account id
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    # # for reading:
    # account_details = AccountSerializer(source='account', read_only=True)
    # for writing:
    reference_account = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(),
        label="Receiver Account",
                                )
    # # for reading
    # reference_account_details = AccountSerializer(source='reference_account', read_only=True)
    class Meta:
        model = Transaction
        fields = ['id', 'account', 'amount', 'transaction_type', 'timestamp', 'reference_account'] # add 'reference_account_details' and 'account_details' for read details


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['is_staff'] = user.is_staff

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        #custom response data
        data['id'] = self.user.id
        data['username'] = self.user.username
        data['password'] = self.user.password

        return data
