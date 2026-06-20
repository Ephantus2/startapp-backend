from rest_framework import serializers
from .models import Task, CompletedTask
from accounts.models import Transactions


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = "__all__"
        
class CompletedSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompletedTask
        fields = "__all__"
        
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transactions
        fields = "__all__"