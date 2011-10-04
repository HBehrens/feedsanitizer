from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse

import sys, traceback
import logging
import StringIO

from time import mktime
from datetime import datetime
import xml.dom.minidom
from misc import fixurl, datetimefromparsed, parseTrueNewsDate

import urllib

import feedparser
feedparser.TIDY_MARKUP = 1
from django.utils import feedgenerator

def buildfeed(url, feed_class, feed_link, ids):
    feed = feedparser.parse(url)      
    result = feed_class(\
        title=feed.feed.title if "title" in feed.feed else None,\
        link=fixurl(feed.feed.link) if "link" in feed.feed else "http://feedsanitizer.appspot.com/",\
        feed_url=fixurl(feed_link),\
        description="", \
        )
        
    uniqueIds = []    
    for entry in feed.entries:
        updated = datetimefromparsed(entry.updated_parsed) if "updated_parsed" in entry else datetime.now()
        entry_link =  entry.link if "link" in entry else entry.links[0]["href"]
        idish = entry.id if "id" in entry else fixurl(entry_link)
        
        # produce unique id
        id = "http://feedsanitizer.appspot.com/id/%s" % (urllib.quote_plus(idish))
        if id in uniqueIds:
            counter = 2
            while "%s-%d" % (id, counter) in uniqueIds:
                counter += 1
            id = "%s-%d" % (id, counter)   
        uniqueIds.append(id)
                
        if len(ids) == 0 or id in ids:
            item = result.add_item( \
              title = entry.title, \
              link = fixurl(entry_link), \
              author_name = entry.author if "author" in entry else "Unknown", \
              description = entry.summary if "summary" in entry else None, \
              pubdate = updated, \
              unique_id = id \
              )
          
    return result
    
FEED_FORMATS = {
    "rss": feedgenerator.Rss201rev2Feed,
    "atom": feedgenerator.Atom1Feed,
    }

def parse_request(request):
    urls = request.GET.getlist("url")
    if len(urls)>0:
        url = urls[0]
    else:
        url = None
        
    output_format = request.GET.get("format", "rss")
    feed_class = FEED_FORMATS[output_format]
    feed_link = "http://%s%s?%s" % ( request.get_host(), reverse("views.sanitize"), request.GET.urlencode() )
    ids = request.GET.getlist("id")
    return (url, output_format, feed_class, feed_link, ids)

def userfriendly(request):
    feed = None
    prettyxml = None
    error = None
    (url, output_format, feed_class, feed_link, ids) = parse_request(request)
    
    if url:
        try:
            feed = buildfeed(url, feed_class, feed_link, ids)
            feedxml = StringIO.StringIO()
            feed.write(feedxml, 'utf-8')
            prettyxml = xml.dom.minidom.parseString(feedxml.getvalue()).toprettyxml()
        except Exception:
            ex = sys.exc_info()
            error = traceback.format_exc()
        
    return render_to_response("home.html", {
        "feed": feed, "feed_xml": prettyxml, "feed_link": feed_link, "feed_format": output_format, 
        "first_url": url, "error": error}
        )

def sanitize(request):
    (url, output_format, feed_class, feed_link, ids) = parse_request(request)

    if not url:
        raise "url not specified"
    feed = buildfeed(url, feed_class, feed_link, ids)

    response = HttpResponse(mimetype=feed.mime_type)
    feed.write(response, 'utf-8')
    return response
    
feedparser.registerDateHandler(parseTrueNewsDate)