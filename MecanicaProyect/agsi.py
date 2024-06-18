import os
import django
from django.conf import settings
from channels.routing import get_default_application

os.environ.setdefault(settings.SECRET_KEY, 'settings.py')
django.setup()
application = get_default_application()