import urllib
import urllib2
from urlparse import urlparse
import re

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup, SoupStrainer
from ftplib import FTP

REC_URL = 'http://www.archive.org/details/%s'
CHECKOUT_URL = 'http://www.archive.org/checkout.php?identifier='

TEMP_ROOT = '/Users/derek/temp/'


LOGIN_URL = 'http://www.archive.org/account/login.php'
TRACK = 'raretunes__an_thou_were_my_ain_thing'

import cookielib
import os.path

COOKIEFILE = '%scookies.txt' % TEMP_ROOT
urlopen = urllib2.urlopen
Request = urllib2.Request
cj = cookielib.LWPCookieJar()

if os.path.isfile(COOKIEFILE):
    # if we have a cookie file already saved
    # then load the cookies into the Cookie Jar
    cj.load(COOKIEFILE)

# if we use cookielib
# then we get the HTTPCookieProcessor
# and install the opener in urllib2
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)



theurl = LOGIN_URL
txdata = urllib.urlencode({ 'username': 'archive@ganzie.com', 'password': 'vienna', 'remember': 'checked' })

"""
theurl = 'http://www.archive.org/account/login.php'
txdata = urllib.urlencode({ 'username': 'archive@ganzie.com', 'password': 'vienna', 'remember': 'CHECKED',
    'referer': 'http://www.archive.org/index.php', 'submit': 'Log in' })



txheaders =  {
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.12) Gecko/20080201 Firefox/2.0.0.12',
    'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
    'Accept-Language': 'en-gb,en;q=0.5',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
    'Referer': 'http://www.archive.org/account/login.php',
    'Content-Type': 'application/x-www-form-urlencoded',
    }
nb content-type this time only ^^^

returned:
These are the cookies we have received so far :
0   :   <Cookie PHPSESSID=add6a5e7c5e48060b2b9d7ea5e3b05f5 for .archive.org/>
1   :   <Cookie logged-in-user=archive%40ganzie.com for .archive.org/>
2   :   <Cookie logged-in-ver=p89x15s6b488b488r19 for .archive.org/>
    
"""
theurl = 'http://www.archive.org/checkout.php?identifier=raretunes__an_thou_were_my_ain_thing'
txdata = None

txheaders =  {
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.12) Gecko/20080201 Firefox/2.0.0.12',
    'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
    'Accept-Language': 'en-gb,en;q=0.5',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
    'Referer': 'http://www.archive.org/detail/raretunes__an_thou_were_my_ain_thing',
    'Cookie': 'logged-in-ver=p89x15s6b488b488r19; logged-in-user=archive%40ganzie.com; PHPSESSID=262b771033981fdd1c57d039196f2190'
    }




print '~~~~~~~~'
try:
    req = Request(theurl, txdata, txheaders)
    # create a request object

    handle = urlopen(req)
    # and open it to return a handle on the url
    ftp_links = SoupStrainer(text=re.compile('.us.archive.org'))
    for link in BeautifulSoup(handle, parseOnlyThese=ftp_links):
        print link

except IOError, e:
    print 'We failed to open "%s".' % theurl
    if hasattr(e, 'code'):
        print 'We failed with error code - %s.' % e.code
    elif hasattr(e, 'reason'):
        print "The error object has the following 'reason' attribute :"
        print e.reason
        print "This usually means the server doesn't exist,",
        print "is down, or we don't have an internet connection."
    sys.exit()

else:
    print 'Here are the headers of the page :'
    print theurl
    print handle.info()
    # handle.read() returns the page
    # handle.geturl() returns the true url of the page fetched
    # (in case urlopen has followed any redirects, which it sometimes does)

print
if cj is None:
    print "We don't have a cookie library available - sorry."
    print "I can't show you any cookies."
else:
    print 'These are the cookies we have received so far :'
    for index, cookie in enumerate(cj):
        print index, '  :  ', cookie
    cj.save(COOKIEFILE)                     # save the cookies again



"""
url = '%s%s' %  (CHECKOUT_URL, TRACK)
print 'opening %s' % url
page = urlopen(url)
print 'open'
#page = urllib2.urlopen('%s%s' %  (CHECKOUT_URL, track))

ftp_links = SoupStrainer(text=re.compile('logged in'))
for link in BeautifulSoup(page, parseOnlyThese=ftp_links):
    print link

#user = soup.find(name='uploader').string
#if user in uploaders:
#    return 0, soup
#else:
#    return 1, 'uploader not recognised: %s' % user
"""
