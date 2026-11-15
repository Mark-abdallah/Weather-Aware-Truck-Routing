from django.db import models


class CachedResponse(models.Model):
    """A provider JSON response, reusable until expires_at."""

    key = models.CharField(max_length=64, primary_key=True)
    payload = models.JSONField()
    expires_at = models.DateTimeField(db_index=True)
