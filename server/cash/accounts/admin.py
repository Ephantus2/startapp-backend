from django.contrib import admin
from .models import ReferralReward
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "phone_number",
        "points",
        "user_wallet",
        "activated",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "activated",
        "is_staff",
        "is_superuser",
        "is_active",
    )

    search_fields = (
        "username",
        "email",
        "phone_number",
        "referral_code",
    )

    readonly_fields = ("referral_code",)

    fieldsets = UserAdmin.fieldsets + (
        (
            "Referral Information",
            {
                "fields": (
                    "referral_code",
                    "referred_by",
                    "points",
                    "user_wallet",
                    "from_referrals",
                    "life_time_earning",
                    "phone_number",
                    "activated",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Additional Information",
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "phone_number",
                    "activated",
                ),
            },
        ),
    )



# Register your models here.
admin.site.register(ReferralReward)