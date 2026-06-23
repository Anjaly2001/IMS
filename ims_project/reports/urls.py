from django.urls import path
from . import views
urlpatterns = [
    path('', views.report_home, name='report_home'),
    path('students/', views.student_report, name='student_report'),
    path('marks/', views.marks_report, name='marks_report'),
    path('organisations/', views.org_report, name='org_report'),
    path('mentors/', views.mentor_report, name='mentor_report'),
    path('pending/', views.pending_report, name='pending_report'),
    path('export/marks/', views.export_marks_excel, name='export_marks_excel'),
]
