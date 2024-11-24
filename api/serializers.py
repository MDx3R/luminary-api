from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Environment

# Create your serializers here.

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True}
        }

class EnvironmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Environment
        fields = ['id', 'name', 'description', 'user', 'createdAt', 'editedAt']
        extra_kwargs = {
            'id': {'read_only': True}
        }

class FileSerializer(serializers.Serializer):
    filename = serializers.CharField(max_length=50)
    file = serializers.FileField()

class FileNameSerializer(serializers.Serializer):
    filename = serializers.CharField(max_length=50)