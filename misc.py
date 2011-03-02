#!/usr/bin/env python
import urlparse, urllib

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