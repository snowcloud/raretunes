from os import path as os_path

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic import list_detail
from django.views.generic.simple import direct_to_template
from tagging.models import Tag

from contact_form.views import contact_form
from scutils.forms import SCContactForm, SimpleStaticSiteContactForm
from scutils.views import external_contact_form

from recordings.models import Artist, Collection
from recordings.views import collections_detail
admin.autodiscover()

latest_performers_info = {
    "queryset": Artist.with_recordings.all().order_by('-date_entered'),
    "paginate_by": 400,
    "template_name" : "recordings/performers_list.html",
    "extra_context": {'latest': True},
}
collections_info = {
    "queryset": Collection.objects.all().filter(status='published'),
    "template_name" : "collections/collections_index.html",
}

urlpatterns = patterns('',
    # Example:
    url(r'^$', direct_to_template, { 'template': 'home/index.html' }, name='home'),

    url(r'^contact/$', contact_form, { 'form_class': SCContactForm }, name='contact'),
    url(r'^contact/sent/$', direct_to_template, { 'template': 'contact_form/contact_form_sent.html' },
        name='contact_form_sent'),
    
    (r'^contact-ext/$', external_contact_form, { 'form_class': SimpleStaticSiteContactForm }),

    (r'^recordings/', include('recordings.urls')),

    url(r'^collections/$', list_detail.object_list, collections_info, name="collections"),        
    url(r'^collections/(?P<slug>[^/]+)', collections_detail, name="collection"),

    url(r'^performers/$', list_detail.object_list, 
        dict(queryset=Artist.objects.all(), 
        paginate_by=400,
        template_name='recordings/performers_list.html' ), name="performers"),
    url(r'^performers/latest/$', list_detail.object_list, latest_performers_info, name="performers-latest"),        
    url(r'^performers/(?P<slug>[^/]+)', list_detail.object_detail, 
        dict(queryset=Artist.objects.all(),
        slug_field='slug',
        template_name='recordings/performers_detail.html'), name="performer"),
        
    url(r'^tags/$', list_detail.object_list,
        dict(queryset=Tag.objects.all(),
        paginate_by=400,
        template_name='tags/tags_index.html',), name="tags"),
    url(r'^tags/(?P<slug>[^/]+)/$', list_detail.object_detail, 
        dict(queryset=Tag.objects.all(), 
        slug_field='name',
        template_name='tags/tags_detail.html', ), name="tag"),

    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(.*)$', 'django.views.static.serve', {'document_root': os_path.join(settings.PROJECT_PATH, 'static')}),
    )
