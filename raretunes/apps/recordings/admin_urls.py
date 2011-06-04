""" admin_urls.py for recordings app

"""

from django.conf.urls.defaults import *
from django.conf import settings
from recordings.models import Recording, Artist

urlpatterns = patterns('recordings.admin_views',
    url(r'^uploads-waiting/$', 'uploads_waiting', name="admin-uploads-waiting"),
    
)
