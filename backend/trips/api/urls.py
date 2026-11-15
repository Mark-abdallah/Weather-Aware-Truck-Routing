from django.urls import path

from trips.api.views import HealthView

urlpatterns = [
    path("health", HealthView.as_view()),
]
