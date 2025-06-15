import os
from django.core.wsgi import get_wsgi_application
from django.conf import settings
from django.contrib.staticfiles.handlers import StaticFilesHandler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'late_log_system.settings')

application = get_wsgi_application()

# Serve static files only when in production and DEBUG is False
if not settings.DEBUG:
    application = StaticFilesHandler(application)
