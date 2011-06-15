from django.conf.urls.defaults import *


urlpatterns = patterns('',
    url(r'^r(?P<short_id>\w+)/$', 'recordings.views.short_recording_detail', name='short-recording'),

)