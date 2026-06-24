# accounts/serializers.py

from rest_framework import serializers
from .models import User, Notifications


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=6
    )

    referred_by_code = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True
    )

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'password',
            'referral_code',
            'points',
            'user_wallet',
            'referred_by_code',
            'phone_number'
        ]
        read_only_fields = [
            'id',
            'referral_code',
            'points',
            'user_wallet'
        ]

    # username validation
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Username already exists"
            )

        if len(value) < 3:
            raise serializers.ValidationError(
                "Username must be at least 3 characters"
            )

        return value

    # email validation
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Email already exists"
            )

        return value

    # referral code validation
    def validate_referred_by_code(self, value):
        if value:
            if not User.objects.filter(
                referral_code=value
            ).exists():
                raise serializers.ValidationError(
                    "Invalid referral code"
                )

        return value

    # general password validation
    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError(
                "Password must be at least 6 characters"
            )

        return value

    def create(self, validated_data):
        referred_by_code = validated_data.pop(
            'referred_by_code',
            None
        )

        referrer = None

        if referred_by_code:
            referrer = User.objects.filter(
                referral_code=referred_by_code
            ).first()

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            referred_by=referrer
        )

        return user
    

class ReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'date_joined'
        ]
        

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Notifications
        fields='__all__'