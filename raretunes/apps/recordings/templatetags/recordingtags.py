from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from tagging.models import Tag

register = template.Library()

@register.inclusion_tag('recordings/recording_item.html')
def show_recording(object):
    return {'recording': object}

@register.inclusion_tag('recordings/tags_display.html')
def show_tags_nolabel(object):
    return {'tag_list': Tag.objects.get_for_object(object), 'label': False}

@register.inclusion_tag('recordings/tags_display.html')
def show_tags(object):
    return {'tag_list': Tag.objects.get_for_object(object), 'label': True}

@register.inclusion_tag('recordings/performers_display.html')
def show_performers(object):
    return {'performers': object.performers.all(), 'label': True}

@register.inclusion_tag('recordings/recording_player.html')
def show_player(object):
    return {'object': object }

@register.filter
def track_link(value):
    return mark_safe('<a href="%s">%s</a>' % (value.play_url, value.title)) 


@register.filter
def archive_details_url(value):
    return settings.ARCHIVE_DETAILS_URL % value.archive_name

@register.filter
def archive_downloads_url(value):
    return settings.ARCHIVE_DOWNLOAD_URL % (value.archive_name, value.title.replace(' ', '').lower())

@register.filter
def archive_stream_url(value):
    return settings.ARCHIVE_STREAM_URL % (value.archive_name, value.archive_name)

@register.filter
def lofi_flash_stream_url(value, arg):
    return """<a href="http://www.archive.org/audio/xspf_player.php?collectionid=%s&amp;playlist=%s_64kb.m3u" onclick="javascript:window.open(this.href,'popup','width=430,height=200,scrollbars=no,resizable=yes,toolbar=no,directories=no,location=no,menubar=no,status=no'); return false;" title="play recording (uses flash player)">%s</a>""" % ( value.archive_name, archive_stream_url(value), arg)

button_template="""<object type="application/x-shockwave-flash" data="%s" width="17" height="17">
<param name="movie" value="%s" />
<img src="noflash.gif" width="17" height="17" alt="" />
</object>
"""

@register.filter
def xspf_button(value):
    data='%smedia/mp_button/musicplayer_f6.swf?song_url=%s_64kb.mp3' % (settings.APP_BASE, archive_stream_url(value))
    return button_template % (data, data)


#ARCHIVE_DOWNLOAD_URL = '%sdownload/raretunes__%%s/%%s' % ARCHIVE_URL
#ARCHIVE_STREAM_URL = '%sdownload/raretunes__%%s/raretunes__%%s' % ARCHIVE_URL

from django.template import Library, Node, TemplateSyntaxError
from recordings.models import Recording, Artist

# eg get_latest news 3 as latest_entries

class LatestContentNode(Node): 
    def __init__(self, item_type, num, varname): 
        self.item_type, self.num, self.varname = item_type, num, varname 
        
    def render(self, context):
        if self.item_type == 'recordings':
            context[self.varname] = Recording.published_recordings.all().order_by('-date_entered')[:self.num]
        elif self.item_type == 'artists':
            context[self.varname] = Artist.objects.all().order_by('-date_entered')[:self.num]
        else:
            raise TemplateSyntaxError, "second argument to get_latest tag must be recordings|artists" 
        return '' 
    
def get_latest(parser, token): 
    bits = token.contents.split() 
    if len(bits) != 5: 
        raise TemplateSyntaxError, "get_latest tag takes exactly four arguments" 
    if bits[3] != 'as': 
        raise TemplateSyntaxError, "third argument to get_latest tag must be 'as'" 
    return LatestContentNode(bits[1], bits[2], bits[4]) 

get_latest = register.tag(get_latest)



@register.filter
def licence(value):
    return settings.LICENCES.get(value, settings.LICENCE_NOT_DEFINED)
