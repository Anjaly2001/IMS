from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    path('', views.assessment_list, name='list'),
    path('viva-marking/<str:student_id>/', views.viva_marking, name='viva_marking'),
    path('mark-entry/', views.mark_entry, name='mark_entry'),
]


