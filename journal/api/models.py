from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class Journal(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='journals'
    )

    def __str__(self):
        return self.title
    
class JournalEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title_uz = models.CharField(max_length=255)
    title_ru = models.CharField(max_length=255, blank=True, null=True)
    title_en = models.CharField(max_length=255, blank=True, null=True)
    content_uz = models.TextField()
    content_ru = models.TextField(blank=True, null=True)
    content_en = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title_uz