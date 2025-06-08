from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from cloudinary.models import CloudinaryField
from datetime import timedelta
from markdownx.models import MarkdownxField

# Create your models here.

# 🗂️ Category model

class Category(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

# 📝 Note model

class Note(models.Model):
    title = models.CharField(max_length=200)
    content = MarkdownxField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    due_date = models.DateField(null=True, blank=True)
    is_pinned = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)

    def days_until_due(self):
        if self.due_date:
            return (self.due_date - timezone.now().date()).days
        return None

    def is_overdue(self):
        return self.due_date and self.due_date < timezone.now().date()

    def is_due_soon(self):
        days = self.days_until_due()
        return days is not None and 0 <= days <= 3

    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = CloudinaryField('image', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'


