from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse

import sys, traceback
import logging
import StringIO
import feedgenerators

from time import mktime
from datetime import datetime
import xml.dom.minidom

import feedparser
from django.utils import feedgenerator

def buildfeed(url, feed_class, feed_link):
    feed = feedparser.parse(url)      

    result = feed_class(\
        title=result.feed.title if "title" in result.feed else "feed title",\
        link=result.feed.link if "link" in result.feed else "feed link",\
        feed_url=feed_link,\
        description="", \
        )
        
    for entry in feed.entries:
        updated = datetime.fromtimestamp(mktime(entry.updated_parsed))
        item = result.add_item( \
          title = entry.title, \
          link = entry.link, \
          description = entry.summary, \
          pubdate = updated, \
          unique_id = entry.id\
          )
        if "author" in entry: 
            item.author_name = entry.author;
          
    return result
    
feed_formats = {
    "rss": feedgenerators.Rss201rev2FeedModified,
    "atom": feedgenerator.Atom1Feed,
    }

def parse_request(request):
    urls = request.GET.getlist("url")
    if len(urls)>0:
        url = urls[0]
    else:
        url = None
        
    format = request.GET.get("format", "rss")
    feed_class = feed_formats[format]
    feed_link = feed_link = "http://%s%s?%s" % ( request.get_host(), reverse("views.sanitize"), request.GET.urlencode() )
    return (url, format, feed_class, feed_link)

def handle_error(request, error):
    return render_to_response("home.html", {
        "error":error
        });

def userfriendly(request):
    feed = None
    prettyxml = None
    error = None
    (url, format, feed_class, feed_link) = parse_request(request)
    
    if url:
        try:
            feed = buildfeed(url, feed_class, feed_link)
            feedxml = StringIO.StringIO()
            feed.write(feedxml, 'utf-8')
            prettyxml = xml.dom.minidom.parseString(feedxml.getvalue()).toprettyxml()
        except Exception:
            e = sys.exc_info()
            error = traceback.format_exc()
        
    return render_to_response("home.html", {
        "feed": feed, "feed_xml": prettyxml, "feed_link": feed_link, "feed_format": format, 
        "first_url": url, "error": error}
        )

def sanitize(request):
    (url, format, feed_class, feed_link) = parse_request(request)

    if not url:
        raise "url not specified"
    feed = buildfeed(url, feed_class, feed_link)

    response = HttpResponse(mimetype=feed.mime_type)
    feed.write(response, 'utf-8')
    return response