from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404

import logging

from time import mktime
from datetime import datetime

import feedparser
from django.utils import feedgenerator

def buildfeed(request):
    """ adapted from feedjack/views.py
    """
    if not "url" in request.GET:
        raise Http404('No URL specified')
        
    url = request.GET.getlist("url")[0]
    result = feedparser.parse(url)      

    format = request.GET.get("format", "rss")
    feedclass = feed_formats[format]
    
    feed = feedclass(\
        title=result.feed.title,\
        link=result.feed.link,\
        feed_url=result.feed.link,\
        description="", \
        )
    for entry in result.entries:
        updated = datetime.fromtimestamp(mktime(entry.updated_parsed))
        feed.add_item( \
          title = entry.title, \
          link = entry.link, \
          description = entry.summary, \
          author_name = entry.author, \
          pubdate = updated, \
          unique_id = entry.id\
          )
          
    return feed

feed_formats = {
    "rss": feedgenerator.Rss201rev2Feed,
    "atom": feedgenerator.Atom1Feed,
    }

def userfriendly(request):
    if "url" in request.GET:
        url = request.GET.getlist("url")
        feed = buildfeed(request)
    return render_to_response("home.html", {"feed": feed, "url": url})

def sanitize(request):
    feed = buildfeed(request)
    response = HttpResponse(mimetype=feed.mime_type)
    feed.write(response, 'utf-8')
    return response