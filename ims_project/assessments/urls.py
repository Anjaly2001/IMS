from django.urls import path
from . import views
urlpatterns = [
    path('internship/<int:internship_pk>/add/', views.mark_create, name='mark_create'),
    path('<int:pk>/edit/', views.mark_edit, name='mark_edit'),
    path('<int:pk>/lock/', views.mark_lock, name='mark_lock'),
    path('summary/<int:student_pk>/', views.marks_summary, name='marks_summary'),
    path('scorecard/<int:student_pk>/', views.student_score_card, name='student_score_card'),
]
