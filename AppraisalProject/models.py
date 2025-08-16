from django.db import models
from django.contrib.auth.models import AbstractUser

class CreateUser(AbstractUser):
    role = models.CharField(max_length=50, choices=[
        ('dean', 'Dean'),
        ('hod', 'Head of Department'),
        ('faculty', 'Faculty'),
    ])

    def __str__(self):
        return self.username
    


class UserProfile(models.Model):
    user = models.OneToOneField(CreateUser, on_delete=models.CASCADE)
    department = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Profile"

