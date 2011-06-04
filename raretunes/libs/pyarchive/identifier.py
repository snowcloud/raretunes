"""
pyarchive.identifier

A Python library which provides an interface for manipulating identifiers
used by the Internet Archive (archive.org).

copyright 2004, Creative Commons, Nathan R. Yergler
"""

__id__ = "$Id: identifier.py 585 2006-06-11 01:50:12Z nyergler $"
__version__ = "$Revision: 585 $"
__copyright__ = '(c) 2004, Creative Commons, Nathan R. Yergler'
__license__ = 'licensed under the GNU GPL2'

import urllib2
import xml.dom.minidom
import string

import exceptions

# valid identifier characters
VALID_CHARS = string.ascii_letters + string.digits + "._"

def conforms(identifier):
    """Checks to make sure the proposed identifier conforms to IA
    standards; returns True if identifier is acceptable; False otherwise."""

    # check length
    if len(identifier) < 5 or len(identifier) > 100:
        return False

    # check alphanumeric-ness
    invalid_chars = [n for n in identifier
                     if n not in VALID_CHARS]
    if len(invalid_chars) > 0:
        return False
    
    # all tests passed -- identifier conforms
    return True

def available(identifier):
    """Checks availability for a given identifier; returns True if the
    identifier is available, False if already in use.  Note that this does
    *not* reserve the identifier, so race conditions may exist."""

    # concatenate the service URL
    checkurl = "http://www.archive.org/services/check_identifier.php?" \
               "identifier=%s" % identifier

    # make request
    try:
        response = urllib2.urlopen(checkurl)
    except urllib2.URLError, e:
        errno = getattr(e, 'errno', None)
        if errno == 10054:
            # connection reset by peer
            # try again
            response = urllib2.urlopen(checkurl)
        else:
            # assume not available
            return False
            
    response_dom = xml.dom.minidom.parse(response)
            
    # parse the response DOM
    result = response_dom.getElementsByTagName("result")[0]
    result_type = result.getAttribute("type")
    result_code = result.getAttribute("code")

    if result_type == 'error':
        raise exceptions.MissingParameterException()
    
    if result_type == 'success' and result_code == 'available':
        return True

    return False

def munge(identifier):
    """Takes a string identifier and returns it, appropriatly munged
    (ie, no spaces, slashes, etc); useful for converting a title to an
    identifier."""

    letters = [n for n in identifier if
               n in VALID_CHARS]

    return "".join(letters)

def verify_url(identifier):
    """Takes an archive.org identifier and returns the verification URL."""

    return "http://www.archive.org/details/%s" % (identifier)

