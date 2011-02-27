from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse

import logging
import StringIO

from time import mktime
from datetime import datetime
import xml.dom.minidom

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
        title=result.feed.title or "feed title",\
        link=result.feed.link or "feed link",\
        feed_url=result.feed.link or "feed link",\
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
    feed = None
    prettyxml = None
    urls = []
    url = None
    logging.debug(reverse("views.sanitize"))
    feed_link = "http://%s%s?%s" % ( request.get_host(), reverse("views.sanitize"), request.GET.urlencode() )
    
    if "url" in request.GET:
        urls = request.GET.getlist("url")
        url = urls[0]
        feed = buildfeed(request)
        feedxml = StringIO.StringIO()
        feed.write(feedxml, 'utf-8')
        prettyxml = xml.dom.minidom.parseString(feedxml.getvalue()).toprettyxml()
        
    return render_to_response("home.html", {"feed": feed, "feed_xml": prettyxml, "feed_link": feed_link, "urls": urls, "first_url": url})

def sanitize(request):
    feed = buildfeed(request)
    response = HttpResponse(mimetype=feed.mime_type)
    feed.write(response, 'utf-8')
    return response