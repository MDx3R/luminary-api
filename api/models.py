from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Environment(models.Model):
    name = models.CharField(max_length = 48)
    description = models.CharField(max_length = 256, blank = True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    createdAt = models.DateTimeField(auto_now_add=True)
    editedAt = models.DateTimeField(auto_now=True)