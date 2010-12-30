from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


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
from shared_apps.recordings.models import Recording, Artist

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


LICENCE_PUBLIC_DOMAIN = '<p>This recording is Public Domain.</p>'
LICENCE_CC_BY_NC_SA_2_5_SCOTLAND = '<!--Creative Commons License--><a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/2.5/scotland/"><img alt="Creative Commons License" style="border-width: 0" src="http://i.creativecommons.org/l/by-nc-sa/2.5/scotland/88x31.png"/></a><br/>These recordings are licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/2.5/scotland/">Creative Commons Attribution-Noncommercial-Share Alike 2.5 UK: Scotland License</a>.<!--/Creative Commons License--><!-- <rdf:RDF xmlns="http://web.resource.org/cc/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"><Work rdf:about=""><license rdf:resource="http://creativecommons.org/licenses/by-nc-sa/2.5/scotland/" /><dc:type rdf:resource="http://purl.org/dc/dcmitype/Sound" /></Work><License rdf:about="http://creativecommons.org/licenses/by-nc-sa/2.5/scotland/"><permits rdf:resource="http://web.resource.org/cc/Reproduction"/><permits rdf:resource="http://web.resource.org/cc/Distribution"/><requires rdf:resource="http://web.resource.org/cc/Notice"/><requires rdf:resource="http://web.resource.org/cc/Attribution"/><prohibits rdf:resource="http://web.resource.org/cc/CommercialUse"/><permits rdf:resource="http://web.resource.org/cc/DerivativeWorks"/><requires rdf:resource="http://web.resource.org/cc/ShareAlike"/></License></rdf:RDF> -->'
LICENCE_CC_BY_SA_3_0 = '<a target="_blank" href="http://creativecommons.org/licenses/by-sa/3.0/" rel="license"><img src="http://i.creativecommons.org/l/by-sa/3.0/88x31.png" alt="Attribution-Share Alike 3.0" style="border: medium none ;"/></a>'
LICENCE_NOT_DEFINED = '<p>Licence not defined.</p>'
LICENCES = { 
    'by-nc-sa_2.5_scotland': LICENCE_CC_BY_NC_SA_2_5_SCOTLAND, 
    'by-sa_3.0': LICENCE_CC_BY_SA_3_0, 
    'public_domain': LICENCE_PUBLIC_DOMAIN
    }

@register.filter
def licence(value):
    return LICENCES.get(value, LICENCE_NOT_DEFINED)
