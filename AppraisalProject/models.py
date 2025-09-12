from django.db import models
from django.contrib.auth.models import AbstractUser

class Department(models.Model):
    departmentName = models.CharField(max_length=100)

    def __str__(self):
        return self.departmentName

class CreateUser(AbstractUser):
    role = models.CharField(max_length=50, choices=[
        ('dean', 'Dean'),
        ('hod', 'Head of Department'),
        ('faculty', 'Faculty'),
    ])
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    reports_to = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="subordinates"
    )

    def __str__(self):
        return self.username



class Activities(models.Model):
   activityName = models.CharField(max_length=100)
  
   def __str__(self):
       return self.activityName

class ActivitySubmission(models.Model):
    user = models.ForeignKey(CreateUser, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    month = models.CharField(max_length=40)
    activity_name = models.ForeignKey(Activities, on_delete=models.CASCADE)
    detail = models.JSONField(default=dict,null=True)
    merged_proof = models.FileField(upload_to="proofs/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)