from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse

import sys, traceback
import logging
import StringIO

from time import mktime
from datetime import datetime
import xml.dom.minidom
from misc import fixurl

import urllib, urllib2
from django.utils import simplejson
from BeautifulSoup import BeautifulSoup

import feedparser
feedparser.TIDY_MARKUP=1
from django.utils import feedgenerator

def buildfeed(url, feed_class, feed_link):
    feed = feedparser.parse(url)      
    logging.debug(feed_link)
    logging.debug(fixurl(feed_link))
    result = feed_class(\
        title=feed.feed.title if "title" in feed.feed else None,\
        link=fixurl(feed.feed.link) if "link" in feed.feed else "http://feedsanitizer.appspot.com/",\
        feed_url=fixurl(feed_link),\
        description="", \
        )
        
    for entry in feed.entries:
        updated = datetime.fromtimestamp(mktime(entry.updated_parsed))
        item = result.add_item( \
          title = entry.title, \
          link = fixurl(entry.link), \
          author_name = entry.author if "author" in entry else None, \
          description = entry.summary, \
          pubdate = updated, \
          unique_id = entry.id\
          )
          
    return result
    
feed_formats = {
    "rss": feedgenerator.Rss201rev2Feed,
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
    feed_link = "http://%s%s?%s" % ( request.get_host(), reverse("views.sanitize"), request.GET.urlencode() )
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
    
def validate(request):
    # read original feed
    url = request.GET.get("url")
    f=urllib2.urlopen(url)
    feed_data=f.read()
    
    # call validator
    params = urllib.urlencode(dict(rawdata=feed_data))
    f=urllib2.urlopen("http://validator.w3.org/feed/check.cgi", params)
    validation_html=f.read()
    
    # validation_html=urllib2.urlopen("http://Heikobehrens.net/misc/feedvalidator.html").read()
    
    #analyzing
    body=BeautifulSoup(validation_html)
    div_main = body.find("div", {"id":"main"})
    h2s = div_main.findAll("h2")
    
    validation_result = {"Sorry":"invalid", "Congratulations!":"valid"}.get(h2s[0].text)
    validation_details = h2s[0].findNextSibling("p").text
    if validation_result == "valid" and validation_details != "This is a valid RSS feed.":
        validation_result = "improvable"
    validation_recommendations = []
    
    if h2s[1].text == "Recommendations":
        recommendations = [r.p.text for r in h2s[1].findNextSibling("ul").findAll("li")]
        validation_recommendations += recommendations
        
    # json
    result = dict(result=validation_result, details=validation_details, recommendations=validation_recommendations)
    jsonresult = simplejson.dumps(result)
    logging.debug(jsonresult)
    return HttpResponse(jsonresult, mimetype='application/json')
    #return HttpResponse(validation_html)
    