from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import resolve

import logging

from django.http import QueryDict

import urllib, urllib2, urlparse
from django.utils import simplejson
from BeautifulSoup import BeautifulSoup
    
def validate(request):
    # read original feed
    url = request.GET.get("url")
    parsedUrl = urlparse.urlparse(url)
    # django cannot handle reentrant calls
    if parsedUrl.netloc == request.get_host():
        chainedRequest = HttpRequest()
        chainedRequest.META = request.META
        chainedRequest.GET = QueryDict(parsedUrl.query, mutable=True)
        #logging.debug(chainedRequest.GET)
        r = resolve(parsedUrl.path)
        #remove HTTP-HEADER
        feed_data = "\n".join(("%s" % r.func(chainedRequest)).split("\n")[2:])
    else:
        f = urllib2.urlopen(url)
        feed_data = f.read()
    
    # call validator
    params = urllib.urlencode(dict(rawdata=feed_data))
    f = urllib2.urlopen("http://validator.w3.org/feed/check.cgi", params)
    validation_html = f.read()
    
    #analyzing
    body = BeautifulSoup(validation_html)
    div_main = body.find("div", {"id":"main"})
    h2s = div_main.findAll("h2")
    validation_result = {"Sorry":"invalid", "Congratulations!":"valid"}.get(h2s[0].text)
    validation_details = h2s[0].findNextSibling("p").text
    validation_recommendations = []
    
    if len(h2s)>=2 and h2s[1].text.startswith("Recom"):
        recommendations = [r.p.text for r in h2s[1].findNextSibling("ul").findAll("li")]
        validation_recommendations += recommendations
        
    if validation_result == "valid" and len(validation_recommendations)>0:
        validation_result = "improvable"
        
        
    # json
    result = dict(result=validation_result, details=validation_details, recommendations=validation_recommendations, feed=url)
    jsonresult = simplejson.dumps(result)
    return HttpResponse(jsonresult, mimetype='application/json')
    #return HttpResponse(validation_html)