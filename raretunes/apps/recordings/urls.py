""" urls.py for recordings app

"""

from django.conf.urls.defaults import *
from django.conf import settings
from recordings.models import Recording, Artist

urlpatterns = patterns('',

    (r'^$', 'django.views.generic.list_detail.object_list', 
        dict(queryset=Recording.published_recordings.all(), 
        template_name='recordings_list.html' )),    
    # (r'^search/$', 'recordings.views.search'),
    (r'^abc/(?P<slug>[^/]+)/$', 'recordings.views.abc'),
    (r'^playlist.xspf$', 'recordings.views.playlist'),
    (r'^player/$', 'recordings.views.player'),
    (r'^process_queues/$', 'recordings.ia_views.process_queues'),
    (r'^(?P<slug>[^/]+)/$', 'django.views.generic.list_detail.object_detail', 
        dict(queryset=Recording.published_recordings.all(),
        slug_field='slug',
        template_name='recordings_detail.html')),    
    )
