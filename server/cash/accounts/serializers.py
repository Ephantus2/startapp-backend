# accounts/serializers.py

from rest_framework import serializers
from .models import User, Notifications

# reset password imports
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from .models import PasswordResetOTP


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
        
# resetting password

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "No account found with this email."
            )

        return value

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    otp = serializers.CharField(
        max_length=6,
        min_length=6
    )

    def validate(self, attrs):

        email = attrs["email"]
        otp = attrs["otp"]

        user = User.objects.filter(email=email).first()

        reset_otp = PasswordResetOTP.objects.filter(
            user=user,
            otp=otp
        ).first()

        if not reset_otp:
            raise serializers.ValidationError(
                {
                    "otp": "Invalid OTP."
                }
            )

        if reset_otp.has_expired():
            raise serializers.ValidationError(
                {
                    "otp": "OTP has expired."
                }
            )

        attrs["user"] = user
        attrs["reset_otp"] = reset_otp

        return attrs
    
class ResetPasswordSerializer(serializers.Serializer):

    email = serializers.EmailField()

    otp = serializers.CharField(
        max_length=6,
        min_length=6
    )

    password = serializers.CharField(
        write_only=True,
        min_length=6
    )

    confirm_password = serializers.CharField(
        write_only=True,
        min_length=6
    )

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):

        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {
                    "confirm_password":
                    "Passwords do not match."
                }
            )

        user = User.objects.filter(
            email=attrs["email"]
        ).first()

        if not user:
            raise serializers.ValidationError(
                {
                    "email":
                    "User does not exist."
                }
            )

        otp = PasswordResetOTP.objects.filter(
            user=user,
            otp=attrs["otp"],
            is_verified=True
        ).first()

        if not otp:
            raise serializers.ValidationError(
                {
                    "otp":
                    "Invalid OTP."
                }
            )

        if otp.has_expired():
            raise serializers.ValidationError(
                {
                    "otp":
                    "OTP has expired."
                }
            )

        attrs["user"] = user
        attrs["otp_object"] = otp

        return attrs

    def save(self):

        user = self.validated_data["user"]

        otp = self.validated_data["otp_object"]

        user.password = make_password(
            self.validated_data["password"]
        )

        user.save()

        otp.delete()

        return user