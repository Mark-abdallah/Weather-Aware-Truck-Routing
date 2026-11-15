from django.urls import path

from trips.api.views import AutosuggestView, HealthView, TripListView

urlpatterns = [
    path("health", HealthView.as_view()),
    path("trips", TripListView.as_view()),
    path("autosuggest", AutosuggestView.as_view()),
]
