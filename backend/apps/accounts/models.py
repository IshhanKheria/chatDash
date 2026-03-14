from django.contrib.auth.models import AbstractUser
from django.db import models
import re


class User(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, default='')
    avatar = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return self.email
