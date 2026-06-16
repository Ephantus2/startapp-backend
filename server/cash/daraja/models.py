from django.db import models
from django.conf import settings

class MpesaPayment(models.Model):
    phone = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    receipt = models.CharField(max_length=30, null=True, blank=True)
    status = models.CharField(max_length=20, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    checkout_id = models.CharField(max_length=100, default=None, unique=True)

    def __str__(self):
        return self.phone