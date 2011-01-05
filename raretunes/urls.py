from os import path as os_path

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from tagging.models import Tag

from contact_form.views import contact_form
from scutils.forms import SCContactForm

from recordings.models import Artist
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^$', 'home.views.index'),

    url(r'^contact/$', contact_form, { 'form_class': SCContactForm }, name='contact_form'),
    url(r'^contact/sent/$', direct_to_template, { 'template': 'contact_form/contact_form_sent.html' },
        name='contact_form_sent'),

    (r'^recordings/', include('recordings.urls')),

    (r'^performers/$', 'django.views.generic.list_detail.object_list', 
        dict(queryset=Artist.objects.all(), 
        paginate_by=400,
        template_name='recordings/performers_list.html' )),    
    url(r'^performers/(?P<slug>[^/]+)', 'django.views.generic.list_detail.object_detail', 
        dict(queryset=Artist.objects.all(),
        slug_field='slug',
        template_name='recordings/performers_detail.html'), name="performer"),    
    url(r'^tags/$', 'django.views.generic.list_detail.object_list',
        dict(queryset=Tag.objects.all(),
        paginate_by=400,
        template_name='tags/tags_index.html',), name="tags"),
    url(r'^tags/(?P<slug>[^/]+)/$', 'django.views.generic.list_detail.object_detail', 
        dict(queryset=Tag.objects.all(), 
        slug_field='name',
        template_name='tags/tags_detail.html', ), name="tag"),

    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(.*)$', 'django.views.static.serve', {'document_root': os_path.join(settings.PROJECT_PATH, 'static')}),
    )
