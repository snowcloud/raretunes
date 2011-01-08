""" urls.py for recordings app

"""

from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic import list_detail
# from django.views.generic import ListView
from recordings.models import Recording, Artist

recording_info = {
    "queryset": Recording.published_recordings.all(),
    "template_name" : "recordings/recordings_list.html"
}
latest_recording_info = {
    "queryset": Recording.published_recordings.all().order_by('-date_entered'),
    "paginate_by": 400,
    "template_name" : "recordings/recordings_list.html",
    "extra_context": {'latest': True},
}


urlpatterns = patterns('',

    url(r'^$', list_detail.object_list, recording_info, name="recordings"),
    url(r'^latest/$', list_detail.object_list, latest_recording_info, name="recordings-latest"),    
    # (r'^search/$', 'recordings.views.search'),
    (r'^abc/(?P<slug>[^/]+)/$', 'recordings.views.abc'),
    (r'^playlist.xspf$', 'recordings.views.playlist'),
    (r'^player/$', 'recordings.views.player'),
    (r'^process_queues/$', 'recordings.ia_views.process_queues'),
    url(r'^(?P<slug>[^/]+)/$', 'django.views.generic.list_detail.object_detail', 
        dict(queryset=Recording.published_recordings.all(),
        slug_field='slug',
        template_name='recordings/recordings_detail.html'),
        name="recording"),    
)
