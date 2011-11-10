""" views for home app

"""

from django.http import HttpResponseRedirect

# from django.shortcuts import render_to_response
# 
# 
# def index(request):
#     return render_to_response('home/index.html')


def rare_fm_home(request):
    return HttpResponseRedirect('http://www.raretunes.org/')
