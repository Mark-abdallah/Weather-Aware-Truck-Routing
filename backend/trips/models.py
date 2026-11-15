import uuid

from django.db import models


class CachedResponse(models.Model):
    """A provider JSON response, reusable until expires_at."""

    key = models.CharField(max_length=64, primary_key=True)
    payload = models.JSONField()
    expires_at = models.DateTimeField(db_index=True)


class Trip(models.Model):
    """A computed trip snapshot: the validated inputs and the plan + heatmap result."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inputs = models.JSONField()
    result = models.JSONField()
    computed_at = models.DateTimeField(auto_now_add=True)
