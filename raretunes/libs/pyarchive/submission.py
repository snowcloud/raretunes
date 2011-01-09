"""
pyarchive.submission

A Python library which provides an interface for uploading files to the
Internet Archive.

copyright 2004-2006, Creative Commons, Nathan R. Yergler
"""

__id__ = "$Id: submission.py 640 2006-06-23 02:34:35Z nyergler $"
__version__ = "$Revision: 640 $"
__copyright__ = '(c) 2004, Creative Commons, Nathan R. Yergler'
__license__ = 'licensed under the GNU GPL2'

import cStringIO as StringIO
import cb_ftp

import httplib
import socket
import urllib
import urllib2
import xml.parsers.expat

import xml.sax.saxutils
import elementtree.ElementTree as etree
import os.path
import string
import types
import codecs
import time

from pyarchive.exceptions import MissingParameterException
from pyarchive.exceptions import SubmissionError
import pyarchive.utils
import pyarchive.identifier
import pyarchive.const
import exceptions

MAX_RETRY = 10

class UploadApplication(object):
    """A class which wraps the relevant information about the 
    uploading application."""
    
    def __init__(self, application_name, application_version):
        self.__name = application_name
        self.__version = application_version
        
    def __getApplication(self):
        return self.__name

    application = property(__getApplication)
    
    def __getVersion(self):
        return self.__version
    
    version = property(__getVersion)

    def __user_agent(self):
        """Returns a user-agent string for this application."""
        return "%s %s" % (self.application, self.version)
    
    user_agent = property(__user_agent)
    
class ArchiveItem:
    """
    <metadata>
      <collection>opensource_movies</collection>
      <mediatype>movies</mediatype>
      <title>My Home Movie</title>
      <runtime>2:30</runtime>
      <director>Joe Producer</director>
    </metadata>    
    """

    # ***
    # old constructor signature:
    # 
    #def __init__(self, uploader, identifier, collection, mediatype,
    #             title, runtime=None, adder=None, license=None):
    # ***
    
    def __init__(self, uploader, license=None):
        """Initialize the submision; uploader should be an instance of 
        UploadApplication"""
        
        self.files = []
        
        self.uploader = uploader
        self.__identifier = None
        self.collection = None
        self.mediatype = None
        self.title = None

        self.metadata = {}
        self.metadata['licenseurl'] = license
            
        self.archive_url = None

    def __setitem__(self, key, value):
        if key == 'subjects':
            subjects = [n.strip() for n in value.split(',')]
            self.metadata['subject'] = subjects
            
        else:
            self.metadata[key] = value

    def __getitem__(self, key):
        return self.metadata[key]

    def __getIdentifier(self):
        """Return the current IA identifier for the submission, or
        None if an identifier has not been successfully set."""
        
        return self.__identifier
        
    def __setIdentifier(self, identifier):
        """Check if the identifier is available by calling create.
        If it is, store the FTP information and return True.  If the
        identifier is not available or does not meet standards, throw
        an exception."""

        if pyarchive.identifier.conforms(identifier) and \
           pyarchive.identifier.available(identifier):

            self.__identifier = identifier
            return True

        raise Exception()

    identifier = property(__getIdentifier, __setIdentifier)
    
    def addFile(self, filename, source, format=None, claim=None):
        self.files.append(ArchiveFile(filename, source, format, claim))

        # set the running time to defaults
        if 'runtime' in self.metadata:
            self.files[-1].runtime = self.metadata['runtime']

        # return the added file object
        return self.files[-1]
    
    def metaxml(self, username=None):
        """Generates _meta.xml to use in submission;
        returns a file-like object."""

        # define a convenience handle to XML escape routine
        xe = xml.sax.saxutils.escape
        
        meta_out = StringIO.StringIO()
        result = codecs.getwriter('UTF-8')(meta_out)

        result.write('<metadata>')

        # write the required keys
        result.write(u"""
        <identifier>%s</identifier>
        <title>%s</title>
        <collection>%s</collection>
        <mediatype>%s</mediatype>
        <resource>%s</resource>
        <upload_application appid="%s" version="%s" />
        """ % (self.identifier,
               xe(self.title),
               self.collection,
               self.mediatype,
               self.mediatype,
               self.uploader.application,
               self.uploader.version) )

        if username is not None:
            result.write(u"<uploader>%s</uploader>\n" % username)
        
        # write any additional metadata
        for key in self.metadata:
            if self.metadata[key] is not None:
                value = self.metadata[key]

                # check if value is a list
                if type(value) in [types.ListType, types.TupleType]:
                    # this is a sequence
                    for n in value:
                        result.write(u'<%s>%s</%s>\n' % (
                                           key,
                                           xe(str(n)),
                                           key)
                                     )
                else:
                    result.write(u'<%s>%s</%s>\n' % (
                                           key,
                                           xe(str(value)),
                                           key) )

        result.write(u'</metadata>\n')

        result.seek(0)
        meta_out.seek(0)
        
        return meta_out
        
    def filesxml(self):
        """Generates _files.xml to use in submission;
        returns a file-like object."""
        
        result = StringIO.StringIO()

        result.write('<files>\n')
        for archivefile in self.files:
            result.write(archivefile.fileNode())
        result.write('</files>\n')

        result.seek(0)
        return result

    def sanityCheck(self):
        """Perform sanity checks before submitting to archive.org"""

        # check for required fields
        if self.identifier is None:
            raise MissingParameterException("No identifier specified.")

        if self.collection is None:
            raise MissingParameterException("No collection specified.")

        if self.mediatype is None:
            raise MissingParameterException("No mediatype specified.")

        if self.metadata['licenseurl'] is None:
            raise MissingParameterException("No licenseurl specified.")
        
        # check that fields were specified
        if len(self.files) < 1:
            raise MissingParameterException("No files selected.")

        # perform sanity checks for each file
        for archivefile in self.files:
            archivefile.sanityCheck()
        

    def createSubmission(self, username, identifier):
        """Create a new submission at archive.org.
        If successful returns a tuple containing (server, path)."""

        retry_count = 0
        
        new_url = "/create.php"
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain",
                   "User-Agent": self.uploader.user_agent}
        
        params = urllib.urlencode({'xml':1,
                                   'user':username,
                                   'identifier':identifier}
                                  )

        conn = httplib.HTTPConnection('www.archive.org')
        conn.request('POST', new_url, params, headers)

        while retry_count < MAX_RETRY:
            try:
                resp = conn.getresponse()
                response = resp.read()

                # successfully read
                break
            except (socket.error, httplib.HTTPException), e:
                # increment the retry count
                retry_count = retry_count + 1

                # short delay to prevent hammering server...
                time.sleep(1)

        # make sure we were successful
        if retry_count == MAX_RETRY:
            # unsuccessful
            raise exceptions.CommunicationsError(
                "Unable to create submission.")
        
        # parse the response
        try:
            result = etree.fromstring(response)
        except xml.parsers.expat.ExpatError, e:
            # XML format error occurred... raise our own Exception
            raise SubmissionError("Invalid response format.", response)
            
        # result = etree.fromstring(response).getroot()
        if result.tag != 'result':
            raise SubmissionError("Unknown response format: %s" %
                                  etree.tostring(result))
            
        if result.attrib['type'] == "success":
            url = result.find('url').text
            print url
            
            return url.split('/') 
        else:
            # some error occured; throw an exception with the message
            raise Exception(result.find('message').text)

    def completeSubmission(self, username):
        """Complete the submission at archive.org; return True if successful,
        otherwise raise an exception."""

        retry_count = 0
        
        # call the import url, check the return result
        importurl = "http://www.archive.org/checkin.php?" \
                    "xml=1&identifier=%s&user=%s" % (self.identifier, username)

        # attempt to complete the submission
        while retry_count < MAX_RETRY:
            try:
                response = etree.parse(urllib2.urlopen(importurl))
                break
            
            except (socket.error, httplib.HTTPException), e:
                # increment the retry count
                retry_count = retry_count + 1

                # short delay to prevent hammering the server
                time.sleep(1)

        # make sure we were successful
        if retry_count == MAX_RETRY:
            # unsuccessful
            raise exceptions.CommunicationsError(
                "Unable to complete submission.")

        # our response should be encapsulated in a <result> tag
        result = response.getroot()
        if result.tag != 'result':
            raise SubmissionError("Unknown response format: %s" %
                                  etree.tostring(result))

        # check the response status
        result_type = result.attrib['type']

        if result_type == 'success':
           # successfully completed
           return True

        else:
           # an error occured; raise an exception
           raise SubmissionError(result.find('message').text)
    
    def submit(self, username, password, server=None, callback=None):
        """Submit the files to archive.org"""

        # set the adder (if necessary)
        if self.metadata.get('adder', None) is None:
            self.metadata['adder'] = username

        # make sure we're ready to submit
        self.sanityCheck()

        # reset the status
        callback.reset(steps=10)

        # create the submission on the server
        ftp_server, ftp_path = self.createSubmission(username, self.identifier)
        
        # connect to the FTP server
        callback.increment(status='connecting to archive.org...')

        ftp = cb_ftp.FTP(ftp_server)
        ftp.login(username, password)
        ftp.cwd(ftp_path)
        
        # upload the XML files
        callback.increment(status='uploading metadata...')

        ftp.storlines("STOR %s_meta.xml" % self.identifier,
                      self.metaxml(username))
        ftp.storlines("STOR %s_files.xml" % self.identifier,
                      self.filesxml())

        # upload each file
        callback.increment(status='uploading files...')

        for archivefile in self.files:
            # determine the local path name and switch directories
            localpath, fname = os.path.split(archivefile.filename)
            os.chdir(localpath)

            # reset the gauge for this file
            callback.reset(filename=archivefile.filename)
            
            ftp.storbinary("STOR %s" % archivefile.archiveFilename(),
                           file(fname, 'rb'), callback=callback)

        ftp.quit()

        # complete the submission
        callback.increment(status='completing upload...')
        if self.completeSubmission(username):
            self.archive_url = pyarchive.identifier.verify_url(self.identifier)
        
        callback.finish()
           
        return self.archive_url
        
class ArchiveFile:
    def __init__(self, filename, source = None, format = None, claim = None):
        # make sure the file exists
        if not(os.path.exists(filename)):
            # can not find the file; raise an exception
            raise IOError
        
        # set object properties from suppplied parameters
        self.filename = filename
        self.runtime = None
        self.source = source
        self.format = format
        self.__claim = claim

        if self.format is None:
            self.__detectFormat()

    def __detectFormat(self):
        info = pyarchive.utils.getFileInfo(os.path.split(self.filename)[1],
                                           self.filename)

        bitrate = info[2]
        if bitrate is not None:
            if bitrate[1]:
                self.format = pyarchive.const.MP3['VBR']
            else:
                try:
                    self.format = pyarchive.const.MP3[bitrate[0]]
                except KeyError, e:
                    self.format = pyarchive.const.MP3['VBR']
                
    def fileNode(self):
        """Generates the XML to represent this file in files.xml."""
        result = '<file name="%s" source="%s">\n' % (
            self.archiveFilename(), self.source)
        
        if self.runtime is not None:
            result = result + '<runtime>%s</runtime>\n' % self.runtime

        # removing metadata dependency for stand-alone-ish-ness
        #if self.__claim is None:
        #    try:
        #        self.__claim = metadata(self.filename).getClaim()
        #    except NotImplementedError, e:
        #        pass
            
        if self.__claim:
            result = result + '<license>%s</license>\n' % \
                     xml.sax.saxutils.escape(self.__claim)
            
        result = result + '<format>%s</format>\n</file>\n' % \
                 xml.sax.saxutils.escape(self.format)

        return result
    
    def sanityCheck(self):
        """Perform simple sanity checks before uploading."""
        # make sure the file exists
        if not(os.path.exists(self.filename)):
            # can not find the file; raise an exception
            raise IOError

        # ensure necessary parameters have been supplied
        if None in (self.filename, self.source, self.format):
            raise MissingParameterException

    def archiveFilename(self):
        localpath, fname = os.path.split(self.filename)
        
        fname = fname.replace(' ', '_')
        chars = [n for n in fname if n in
                 (string.ascii_letters + string.digits + '._')]
        
        result = "".join(chars)
        if result[0] == '.':
            # the first character is a dot,
            # indicating there's nothing before the extension.
            result = '%s%s' % (hash(result), result)

        return result
    
    
        
        
        

