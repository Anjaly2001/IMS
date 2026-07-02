from django.urls import path
from . import views
urlpatterns = [
    path('', views.internship_list, name='internship_list'),
    path('create/', views.internship_create, name='internship_create'),
    path('<int:pk>/', views.internship_detail, name='internship_detail'),
    path('<int:pk>/edit/', views.internship_edit, name='internship_edit'),
    path('<int:pk>/documents/', views.internship_upload_documents, name='internship_upload_documents'),
    path('<int:pk>/verify/', views.internship_verify, name='internship_verify'),
    path('mentors/', views.mentor_list, name='mentor_list'),
    path('mentor/assign/', views.mentor_assign, name='mentor_assign'),
    path('mentor/assign/<int:student_pk>/', views.mentor_assign, name='mentor_assign_student'),
]
