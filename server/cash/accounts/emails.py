from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string

from .models import PasswordResetOTP


def send_password_reset_otp(user):
    """
    Generates a new OTP, deletes any previous OTPs,
    saves the new one and sends it via email.
    """

    # Delete previous OTPs
    PasswordResetOTP.objects.filter(user=user).delete()

    # Generate new OTP
    otp = PasswordResetOTP.objects.create(
        user=user,
        otp=PasswordResetOTP.generate_otp(),
        expires_at=PasswordResetOTP.expiry_time()
    )

    subject = "Reset Your Password"

    context = {
        "username": user.username,
        "otp": otp.otp
    }

    html_content = render_to_string(
        "emails/password_reset_otp.html",
        context
    )

    email = EmailMultiAlternatives(
        subject=subject,
        body="Your password reset code is {}".format(otp.otp),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )

    email.attach_alternative(
        html_content,
        "text/html"
    )

    email.send()

    return otp