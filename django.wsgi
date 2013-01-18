import os, sys

sys.path.append('/srv/insta.gangverk.is/hashtagtest')
sys.path.append('/usr/local/lib/python2.7/dist-packages/django/')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hashtagtest.settings")

print "Setting up django WSGI environment"
print sys.path

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
