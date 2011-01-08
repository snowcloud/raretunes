""" shared_apps.recordings.views

"""
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import Context, loader
from recordings.models import Recording, Collection, COLLECTION_TEMPLATE_DEFAULT

# def search(request):
#     objects = None
#     error_msg = ''
#     terms = request.REQUEST.get('terms', '').strip()
#     if terms == '':
#         error_msg = 'enter some text to search for in the box, and try again.'
#     else:
#         objects = Recording.searcher.search(terms)
#         if not objects:
#             #try a boolean seach instead
#             objects = Recording.published_recordings.filter(note__search=terms)
#         
#     return render_to_response('recordings/search_results.html', { 'terms': terms, 'error_msg': error_msg, 'objects': objects })

def collections_detail(request, slug):
    """docstring for collection"""
    o = get_object_or_404(Collection.objects.filter(status='published'), slug=slug)
    
    template = getattr(o, 'template', COLLECTION_TEMPLATE_DEFAULT)
    
    return render_to_response(template, {'object': o, 'items': o.items.order_by('collectionitem__order')})
    

def abc(request, slug):
    o = get_object_or_404(Recording.published_recordings, slug=slug)
    if not o.abc:
        raise Http404
        
    return HttpResponse(o.abc, mimetype="text")

def playlist(request):
    t = loader.get_template('recordings/playlist.xml')
    tracks = []
    
    #l = request.GET.get('l', 'nope')
    if 'l' in request.GET:
        ids = request.GET['l'].split(',')
        for i in ids:
            try:
                r = get_object_or_404(Recording.published_recordings, pk__exact=i)
                tracks.append(r)
            except Http404:
                pass
    c = Context({ 'tracks': tracks })
    return HttpResponse(t.render(c), mimetype="text/xml")

def player(request):
    c = Context({ 'sel_tracks': request.GET.get('l', '') })
    return render_to_response('recordings/player.html', c)

