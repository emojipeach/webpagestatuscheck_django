import uuid
from django.db import models

class Site(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.CharField(max_length=255)
    was_checked = models.IntegerField(default=0)
    was_up = models.IntegerField(default=0)
    status = models.CharField(max_length=20)
    uptime = models.DecimalField(decimal_places=2, max_digits=5, default=0)
    
    def __str__(self):
        return self.url