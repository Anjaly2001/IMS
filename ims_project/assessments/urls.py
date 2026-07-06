from django.urls import path
from . import views

urlpatterns = [
    path('internship/<int:internship_pk>/add/', views.marks_entry, name='marks_entry'),
    path('<int:pk>/review/', views.marks_review, name='marks_review'),
    path('summary/<int:student_pk>/', views.marks_summary, name='marks_summary'),
    path('scorecard/<int:student_pk>/', views.student_score_card, name='student_score_card'),
    path('scorecard/<int:student_pk>/pdf/', views.student_score_card_pdf, name='student_score_card_pdf'),
    path('internship/<int:internship_pk>/intermediate/add/', views.intermediate_mark_add, name='intermediate_mark_add'),
    path('intermediate/<int:pk>/edit/', views.intermediate_mark_edit, name='intermediate_mark_edit'),
]
