from django.urls import path
from .views import DashboardBaseView

app_name = 'apps.dashboard'

urlpatterns = [
    path('', DashboardBaseView.as_view(), name='dashboard'),
]