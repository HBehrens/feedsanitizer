#!/usr/bin/env python
import urlparse, urllib
from datetime import datetime, tzinfo
from time import mktime, strptime
import feedparser

def datetimefromparsed(tuple):
    try:
        return datetime.fromtimestamp(mktime(tuple))
    except:
        return None
        
_TrueNewsDateFormat = "%A: %m:%d:%Y: %H:%M:%S"
def parseTrueNewsDate(dateString):
    dateString = " ".join(dateString.split(" ")[0:3])
    return strptime(dateString, _TrueNewsDateFormat)

def fixurl(url):
    """
    adapted from
    http://stackoverflow.com/questions/804336/best-way-to-convert-a-unicode-url-to-ascii-utf-8-percent-escaped-in-python/804380#804380
    """
    # turn string into unicode
    if not isinstance(url,unicode):
        url = url.decode('utf8')

    # parse it
    parsed = urlparse.urlsplit(url)

    # divide the netloc further
    userpass,at,hostport = parsed.netloc.partition('@')
    if not hostport:
        hostport, userpass = userpass, hostport
        
    user,colon1,pass_ = userpass.partition(':')
    host,colon2,port = hostport.partition(':')

    # encode each component
    scheme = parsed.scheme.encode('utf8')
    user = urllib.quote(user.encode('utf8'))
    colon1 = colon1.encode('utf8')
    pass_ = urllib.quote(pass_.encode('utf8'))
    at = at.encode('utf8')
    host = host.encode('idna').lower()
    colon2 = colon2.encode('utf8')
    port = port.encode('utf8')
    path = '/'.join(  # could be encoded slashes!
        urllib.quote(urllib.unquote(pce).encode('utf8'),'')
        for pce in parsed.path.split('/')
    )
    if not path:
        path = "/"
    #query = urllib.quote(urllib.unquote(parsed.query).encode('utf8'),'=&?/')
    #fragment = urllib.quote(urllib.unquote(parsed.fragment).encode('utf8'))
    query = parsed.query
    fragment = parsed.fragment
    
    # put it back together
    netloc = ''.join((user,colon1,pass_,at,host,colon2,port))
    return urlparse.urlunsplit((scheme,netloc,path,query,fragment))
    
import unittest
    
class Tests(unittest.TestCase):
    def testTrueNewsDateFormat(self):
        self.assertEqual("Friday: 01:29:2010: 17:30:18", datetime(2010, 01, 29, 17, 30, 18).strftime(_TrueNewsDateFormat))
        dt = datetime.strptime("Friday: 1:29:2010: 17:30:18", _TrueNewsDateFormat)
        self.assertEqual(dt, datetime(2010, 01, 29, 17, 30, 18))

    def testParseTrueNewsDateFormat(self):
        r = parseTrueNewsDate("Friday: 1:29:2010: 17:30:18 GMT -05:00")
        self.assertEquals(r, (2010, 1, 29, 17, 30, 18, 4, 29, -1))

    def testDate(self):
        def t(dateString):
            t = feedparser._parse_date(dateString)
            return datetimefromparsed(t).isoformat() if t else None
            
            
        self.assertEqual(t("Wed, 17 Aug 2011 12:25:03 +0100"), "2011-08-17T12:25:03")
        self.assertEqual(t("Mon, 18 Apr 2011 17:30:18 GMT -05:00"), "2011-04-18T18:30:18")
        
        self.assertEqual(t("Friday: 1:29:2010: 17:30:18 GMT -05:00"), None)
        feedparser.registerDateHandler(parseTrueNewsDate)
        self.assertEqual(t("Friday: 1:29:2010: 17:30:18 GMT -05:00"), "2010-01-29T17:30:18")
        feedparser._date_handlers.remove(parseTrueNewsDate)

    def testPaths(self):
        self.assertEquals(fixurl("http://localhost:8000/sanitize?url=http%3A%2F%2Fwww.planeteclipse.org%2Fplanet%2Frss20.xml&format=rss"), "http://localhost:8000/sanitize?url=http%3A%2F%2Fwww.planeteclipse.org%2Fplanet%2Frss20.xml&format=rss")
        self.assertEquals(fixurl("http://HeikoBehrens.net"), "http://heikobehrens.net/")
        self.assertEquals(fixurl("http://User@HeikoBehrens.net"), "http://User@heikobehrens.net/")
        
def _test():
    import doctest, misc
    doctest.testmod(misc)
    unittest.main()

if __name__ == '__main__':
    _test()    