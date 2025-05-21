from django.db import models
from django.utils.timezone import now
from datetime import timedelta

class c(models.Model):
    flag = models.IntegerField()
    def __str__(self) -> str:
        return f"{self.flag}"