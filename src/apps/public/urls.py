from django.urls import path
from . import views

app_name = 'apps.public'

urlpatterns = [
    path('contactus/', views.ContactUsView.as_view(), name='contactus'),
    path('contact_list/', views.ContactUsListView.as_view(), name='contact_list'),
    path('contact_reply/<int:pk>/', views.ContactUsReplyView.as_view(), name='contact_reply'),
    path('about/', views.AboutUsView.as_view(), name='about'),
    path('help/', views.HelpView.as_view(), name='help'),
]
