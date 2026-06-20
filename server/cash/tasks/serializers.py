from rest_framework import serializers
from .models import Task, CompletedTask


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = "__all__"
        
class CompletedSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompletedTask
        fields = "__all__"