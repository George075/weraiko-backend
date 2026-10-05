from django.urls import path
from . import views

urlpatterns = [
    path('job/<slug:slug>/', views.job_page, name='job_page'),
    path('jobs/education/<slug:slug>/', views.education_jobs, name='education_jobs'),
    path('jobs/category/<slug:slug>/', views.category_jobs, name='category_jobs'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'),
    path('jobs/<int:pk>/apply/', views.job_apply, name='job_apply'),
    path('guides/', views.guide_list, name='guide_list'),
    path('guides/<slug:slug>/', views.guide_detail, name='guide_detail'),
    path('jobs/location/<slug:slug>/', views.location_jobs, name='location_jobs'),
]
