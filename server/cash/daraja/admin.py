from django.contrib import admin

# Register your models here.
from .models import Withdrawal, B2CCallbackLog

admin.site.register(Withdrawal)
admin.site.register(B2CCallbackLog)