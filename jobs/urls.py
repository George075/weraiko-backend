from django.urls import path
from . import views

urlpatterns = [
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'),
    path('jobs/<int:pk>/apply/', views.job_apply, name='job_apply'),

    path('guides/', views.guide_list, name='guide_list'),
    path('guides/<slug:slug>/', views.guide_detail, name='guide_detail'),
]