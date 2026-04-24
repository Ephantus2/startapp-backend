from rest_framework import serializers
from django.contrib.auth.models import User
import re

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)
    confirm_password = serializers.CharField(write_only = True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']
        
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('username already exists')
        return value
    
    def validate_email(self, value):
        email_regex = r'^[A-Za-z0-9._-]+@[A-Za-z0-9._-]+\.[A-Za-z0-9._-]+$'
        if not re.match(email_regex, value):
            raise serializers.ValidationError('Enter a valid email address')
        
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('email already exists')
        return value
    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if password != confirm_password:
            raise serializers.ValidationError('passwords do not match')
        if not re.search(r'[A-Z]', password):
            raise serializers.ValidationError({'password': 'password Must contain capital letter'})
        if not re.search(r'\d', password):
            raise serializers.ValidationError({'password': 'password must contain a number'})
        if not re.search(r'[.-_$,#!@:;?/*&]', password):
            raise serializers.ValidationError({'password': 'password must contain a special character'})
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        
        user = User.objects.create_user(
            username= validated_data['username'],
            email= validated_data['email'],
            password= validated_data['password']
        )
        
        return user