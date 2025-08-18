from django.urls import path

from . import views

app_name = 'apps.job'


urlpatterns = [
    path('', views.JobListView.as_view(), name='job_list'),
    path('jobs/<int:pk>/', views.JobDetailView.as_view(), name='job_detail'),

    path('create/', views.JobCreateView.as_view(), name='create'),
    path('my-jobs/', views. EmployerJobListView.as_view(), name='employer-job-list'),
    path('employer/applications/', views.EmployerApplicationListView.as_view(), name='employer_applications'),
    path('employer/accepted-jobs/', views.EmployerAcceptedJobsView.as_view(), name='employer_accepted_jobs'),
    path('applications/<int:pk>/approve/', views.ApplicationApproveView.as_view(), name='application_approve'),
    path('applications/<int:pk>/reject/', views.ApplicationRejectView.as_view(), name='application_reject'),
    path('employer/jobs/<int:pk>/delete/', views.EmployerJobDeleteView.as_view(), name='employer_job_delete'),
    path('employer/jobs/<int:pk>/edit/', views.EmployerJobUpdateView.as_view(), name='employer_job_edit'),

    path('jobs/<int:pk>/apply/', views.JobApplyView.as_view(), name='job_apply'),
    path('my-applications/', views.MyApplicationsView.as_view(), name='my_applications'),
    path('applications/<int:pk>/cancel/', views.CancelApplicationView.as_view(), name='cancel_application'),
]
