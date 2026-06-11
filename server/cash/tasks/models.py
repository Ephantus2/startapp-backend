from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings


class Task(models.Model):

    TASK_TYPES = (
        ('youtube_watch', 'Watch YouTube Video'),
        ('website_visit', 'Visit Website'),
        ('quiz', 'Quiz'),
        ('daily_login', 'Daily Login'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()

    task_type = models.CharField(
        max_length=30,
        choices=TASK_TYPES
    )

    reward_points = models.IntegerField(default=0)

    url = models.URLField(blank=True, null=True)

    required_seconds = models.IntegerField(default=30)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class CompletedTask(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE
    )

    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'task')