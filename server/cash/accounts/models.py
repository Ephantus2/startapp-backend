# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    referral_code = models.CharField(max_length=12, unique=True, blank=True)
    referred_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='people_referred'
    )
    points = models.IntegerField(default=0)
    user_wallet = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.referral_code:
            while True:
                code = str(uuid.uuid4()).replace('-', '')[:10].upper()
    
                if not User.objects.filter(referral_code=code).exists():
                    self.referral_code = code
                    break
    
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"username: {self.username}, email: {self.email}"


class ReferralReward(models.Model):
    referrer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='rewards_given'
    )
    new_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='rewards_received'
    )
    points = models.IntegerField(default=100)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.referrer.username} referred {self.new_user.username}"
    
class Wallet(models.Model):
    balance = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
class Activate(models.Model):
    activated = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)