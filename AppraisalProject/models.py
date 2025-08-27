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


class Department(models.Model):
    departmentName = models.CharField(max_length=100)

    def __str__(self):
        return self.departmentName

class Activities(models.Model):
   activityName = models.CharField(max_length=100)
  
   def __str__(self):
       return self.activityName

class ActivitySubmission(models.Model):
    user = models.ForeignKey(CreateUser, on_delete=models.CASCADE)
    department = models.CharField(max_length=120)
    month = models.CharField(max_length=40)
    activity_name = models.CharField(max_length=120)
    detail = models.JSONField(default=dict,null=True)
    merged_proof = models.FileField(upload_to="proofs/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)