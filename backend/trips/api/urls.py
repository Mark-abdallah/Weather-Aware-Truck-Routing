from django.urls import path

from trips.api.views import AutosuggestView, HealthView, TripDetailView, TripListView

urlpatterns = [
    path("health", HealthView.as_view()),
    path("trips", TripListView.as_view()),
    path("trips/<uuid:trip_id>", TripDetailView.as_view()),
    path("autosuggest", AutosuggestView.as_view()),
]
