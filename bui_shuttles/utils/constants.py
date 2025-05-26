from django.utils import timezone
from django.db import models

class TimeStampModel(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False, )
    modified = models.DateTimeField(auto_now=True, blank=True, null=True)

    
    class Meta:
        abstract = True


    