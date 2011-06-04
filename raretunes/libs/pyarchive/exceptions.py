"""
pyarchive.exceptions

A Python library which provides an interface for uploading files to the
Internet Archive.

copyright 2004, Creative Commons, Nathan R. Yergler
"""

__id__ = "$Id: exceptions.py 606 2006-06-14 19:58:22Z nyergler $"
__version__ = "$Revision: 606 $"
__copyright__ = '(c) 2004, Creative Commons, Nathan R. Yergler'
__license__ = 'licensed under the GNU GPL2'


class MissingParameterException(LookupError):
    pass

class SubmissionError(Exception):
    pass
    
class CommunicationsError(Exception):
    pass
