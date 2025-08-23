from django.urls import path

from . import views

app_name = 'apps.notification'


urlpatterns = [
    path('', views.NotificationsViews.as_view(), name='notifications')
]
