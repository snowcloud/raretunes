from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

from os import path as os_path

admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^$', 'home.views.index'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(.*)$', 'django.views.static.serve', {'document_root': os_path.join(settings.PROJECT_PATH, 'static')}),
    )
