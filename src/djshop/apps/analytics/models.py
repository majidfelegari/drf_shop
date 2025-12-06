from django.db import models
from django.contrib.admin.models import LogEntry

# Create your models here.

# for interaction user
# class FootPrint(models.Model):
#     pass

class ActionHistory(LogEntry):
    class Meta:
        proxy = True