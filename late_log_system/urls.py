# late_log_system/urls.py

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect  # Import the redirect function
from django.conf import settings
from django.conf.urls.static import static
from logs import views  # Import views from the 'logs' app

# Define the view to redirect to the 'register_student' view
def home(request):
    return redirect('/admin/')  # Redirect root URL to the admin page directly

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logs/', include('logs.urls')),  # Include the 'logs' app URLs
    path('scan/', views.scan_qr, name='scan_qr'),
    path('home/', views.index, name='index'),  # Main page (instead of the root)
    path('', lambda request: redirect('login')),  # Root URL redirects to login page
    path('logs/login/', views.login_view, name='login'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
