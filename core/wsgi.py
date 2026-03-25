"""
WSGI config for qr_service project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from pathlib import Path
from tools_box.config.settings import CoreConfigReader
from django.core.wsgi import get_wsgi_application

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CoreConfigReader(file_path=str(BASE_DIR / ".env"))

environment = CoreConfigReader.get_config("ENVIRONMENT", default="local")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'core.settings.{environment}')

application = get_wsgi_application()
