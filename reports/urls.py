from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_list, name='list'),
    path('diary-review/<str:student_id>/', views.diary_review, name='review'),
    path('diary-review/<str:student_id>/week/<int:week_num>/', views.diary_detail, name='detail'),
]

