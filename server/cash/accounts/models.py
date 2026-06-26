# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

from django.conf import settings


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
    from_referrals = models.IntegerField(default=0)
    life_time_earning = models.IntegerField(default=0)
    phone_number = models.CharField(default="0712345678", max_length=15)
    activated = models.BooleanField(default=True)
    

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
    
class Transactions(models.Model):
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )    

    TYPES = (
        ('task', 'task'),
        ('referral', 'referral'),
        ('withdrawal', 'withdrawal'),
        ('deposit', 'deposit'),
    )
    description = models.TextField()

    task_type = models.CharField(
        max_length=30,
        choices=TYPES
    )
    STATUS_CHOICES = (
        ('pending', 'pending'),
        ('completed', 'completed'),
        ('failed', 'failed'),
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
class Wallet(models.Model):
    balance = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
class Activate(models.Model):
    activated = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
class Notifications(models.Model):
    NOTIF_TYPES = (
        ('task', 'task'),
        ('referral', 'referral'),
        ('withdrawal', 'withdrawal'),
        ('system', 'system')
    )

    notif_types = models.CharField(
        max_length=30,
        choices=NOTIF_TYPES,
        default='system'
    )
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)