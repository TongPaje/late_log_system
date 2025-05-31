# logs/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Root URL that redirects to the login page
    path('', views.home, name='home'),  
    
    # Login page URL
    path('login/', views.login_view, name='login'),  
    
    # Main page URL after login (protected by login_required decorator)
    path('home/', views.index, name='index'),  

    # Student Registration Form
    path('students/', views.view_students, name='students'),
    path('register/', views.register_student, name='register_student'),
    # Other page URL
    path('students/', views.view_students, name='view_students'), 
    path('students/edit/<int:student_id>/', views.edit_student, name='edit_student'),
    path('scan/', views.scan_qr, name='scan_qr'),
    path('view_reports/', views.view_reports, name='view_reports'),
    path('chart_reports/', views.chart_reports, name='chart_reports'),
    path('export/', views.export_report, name='export_report'),
    path('students/export/', views.export_student_list, name='export_student_list'),
    path('logout/', views.logout_view, name='logout'),
 
   
]
