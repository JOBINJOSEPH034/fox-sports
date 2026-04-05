"""
WSGI config for fox project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fox.settings')

application = get_wsgi_application()

# Auto-create the database cache table on cold-start if it doesn't exist.
# This is needed on Vercel since build.sh doesn't run in the Python lambda context.
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_name = 'cache_table' LIMIT 1"
        )
        if not cursor.fetchone():
            from django.core.management import call_command
            call_command('createcachetable', verbosity=0)
except Exception:
    pass  # Fail silently — never crash the app over cache table creation

