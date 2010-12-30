""" 
ia-py.py
python module for Internet Archive, archive.org
(c) Derek Hoy, March 2008
"""
import urllib
import urllib2
import cookielib
from urlparse import urlparse
import re
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup, SoupStrainer
from ftplib import FTP
import sys, os

IA_HOST = 'http://www.archive.org/'
LOGIN_URL = '%saccount/login.php' % IA_HOST
CHECKIN_URL = '%scheckin/' % IA_HOST
# CHECKOUT_URL = '%scheckout.php?identifier=' % IA_HOST
CHECKOUT_URL = '%sedit/' % IA_HOST
# eg. http://www.archive.org/edit/raretunes_333_great-cause-my-sorrow
DOWNLOAD_URL = '%sdownload/' % IA_HOST

CHECKOUT_LINK = '.us.archive.org/'
UPDATE_METADATA_URL = '%seditxml.php' % IA_HOST

RESULT_ERROR = 0
RESULT_OK = 1
#RESULT_STRINGS = ('OK', 'Error')

from logging import log, ERROR, INFO, DEBUG

"""
CRITICAL    50
ERROR   40
WARNING     30
INFO    20
DEBUG   10
NOTSET  0
"""

DEF_HEADERS =  {
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.12) Gecko/20080201 Firefox/2.0.0.12',
    'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
    'Accept-Language': 'en-gb,en;q=0.5',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
    }

# login could add these, but seems OK without them...
#txheaders =  {
#    'Referer': LOGIN_URL,
#    'Content-Type': 'application/x-www-form-urlencoded',
#    }
#txheaders.update(DEF_HEADERS)

class IAConnectionError(Exception):
    pass

###############################################################
class IAConnection(object):
    """
    Login object holds info on user, password and authentication data
    returns dict- PHPSESSID, logged-in-user, logged-in-ver 
    """

    ###############################################################
    def _log(self, level, message):
        if self.logger:
            self.logger.log(level, message)

    ###############################################################
    def __init__(self, username=None, password=None, logger=None):
        self.username = username
        self.password = password
        self.logger = logger
        self.cookies = None
        self.uploaders = {}
        self._log(DEBUG, 'IAConnection created')

    ###############################################################
    def _get_page(self, url, txdata=None, txheaders=None):
        
        if not txheaders:
            txheaders = DEF_HEADERS 
        try:
            req = urllib2.Request(url, txdata, txheaders)
            self._log(DEBUG, 'request method: %s' % req.get_method())
            page = urllib2.urlopen(req)
        
        except IOError, e:
            raise IAConnectionError('get page failed: %s - %s' % (url, str(e)))
            """
            result = ResultSet(RESULT_ERROR, 'failed to open "%s".' % url)
            if hasattr(e, 'code'):
                result = ResultSet(RESULT_ERROR, 'failed to get "%s" - error code: %s.' % (url, e.code))
            elif hasattr(e, 'reason'):
                result = ResultSet(RESULT_ERROR, 'failed to get "%s" - reason: %s.' % (url, e.reason))
            result.log(ERROR, self.logger)
            """
        return page
            
    ###############################################################
    def login(self, username=None, password=None):
        """
        If username or password is given, both must be given
        Login and get authentication data: PHPSESSID, logged-in-user, logged-in-ver
        Returns tuple error code, message
        On success, error code= 0, message holds cookie string 
        """
        if username and password:
            if self.username != username:
                self.logout()
                self.username = username
                self.password = password
        
        if self.logged_in():
            self._log(DEBUG, 'Already logged in as %s' % self.username)
        
        cj = cookielib.LWPCookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)
        txdata = urllib.urlencode(
            {'username': self.username,
             'password': self.password,
             'remember': 'CHECKED',
             'referer': IA_HOST,
             'submit': 'Log in' }
        )
        self._log(DEBUG, 'logging in as %s' % self.username)
        self._get_page(LOGIN_URL, {}) # call blank form to set cookies first
        self._get_page(LOGIN_URL, txdata)
        
        #print 'These are the cookies we have received so far :'
        #for index, cookie in enumerate(cj):
        #    print index, '  :  ', cookie, ' - ' , cookie.expires

        self.cookies = '; '.join(['%s=%s' % (cookie.name, cookie.value) for cookie in cj])
        if self.logged_in():
            self._log(DEBUG, 'Logged in as %s' % self.username)
        else:
            raise IAConnectionError('login failed')

    ###############################################################
    def logged_in(self):
        """
        archive.org puts cookies valid for 1 year with 'remember me'
        so a login before any other access function should be good for that long :)
        """
        return self.cookies and self.cookies.find('logged-in-user') > -1
    
    ###############################################################
    def logout(self):
        self.cookies = None
    
    ###############################################################
    def checkin(self, rec_id):
        if not self.logged_in():
            raise IAConnectionError('not logged in')
            #result = ResultSet(RESULT_ERROR, 'not logged in')
            #return result.log(ERROR, self.logger)
        txheaders = { 'Cookie': self.cookies }
        txheaders.update(DEF_HEADERS)   
        self._get_page('%s%s' % (CHECKIN_URL, rec_id ), None, txheaders)
        #if result.resultCode == RESULT_OK:
        #    result = ResultSet(RESULT_OK, 'checked in %s' % rec_id, rec_id)
        #return result.log(INFO, self.logger)
        self._log(INFO, 'checked in %s' % rec_id)

    ###############################################################
    def checkout(self, rec_id):
        
        if not self.logged_in():
            raise IAConnectionError('not logged in')
            #result = ResultSet(RESULT_ERROR, 'not logged in')
            #return result.log(ERROR, self.logger)
        txheaders = { 'Cookie': self.cookies }
        txheaders.update(DEF_HEADERS)
        self._log(INFO, 'checking out %s' % rec_id)
        page = self._get_page('%s%s' % (CHECKOUT_URL, rec_id ), None, txheaders)
        #if result.resultCode != RESULT_OK:
        #    result = ResultSet(RESULT_ERROR, 'checkout failed for %s' % rec_id)
        #    return result.log(ERROR, self.logger)
        
        link = None
        links = SoupStrainer('a', href=re.compile(CHECKOUT_LINK))
        # self._log(INFO, 'links %s' % links)
        soup = BeautifulSoup(page, parseOnlyThese=links)
        # self._log(INFO, 'soup %s' % soup)
        if len(soup) > 0:
            link = soup.contents[0]['href']
        if link:
            #result = ResultSet(RESULT_OK, 'checked out %s' % link, link)
            #result.log(INFO, self.logger)
            self._log(INFO, 'checked out %s (link: %s)' % (rec_id, link))
            return link
        else:
            raise IAConnectionError('checkout failed for %s'  % rec_id)

    ###############################################################
    def get_uploader(self, rec_id):
    
        if not rec_id:
            raise IAConnectionError('get_uploader failed - rec_id is None')
        url = "http://www.archive.org/download/%s/%s_meta.xml"
        try:
            page = urllib2.urlopen(url %  (rec_id, rec_id))
            soup = BeautifulStoneSoup(page)
            uploader = soup.find(name='uploader')
            if uploader:
                user = uploader.string
            else:
                raise IAConnectionError('metadata not found for %s (uploader not found)' % rec_id)
            if self.uploaders.has_key(user):
                self._log(DEBUG, 'found uploader: %s' % user)
            else:
                #result = ResultSet(RESULT_ERROR, 'uploader not recognised for %s' % rec.slug)
                #result.log(ERROR, self.logger)
                
                self._log(DEBUG, 'unknown uploader: %s' % user)
                return None
                #TODO allow unknown uploaders
                #raise IAConnectionError('uploader "%s" not recognised for %s' % (user, rec_id))
    
        except urllib2.HTTPError:
            raise IAConnectionError('metadata not found for %s' % rec_id)
            #result = ResultSet(RESULT_ERROR, 'metadata not found for %s' % rec.slug)
            #return result.log(ERROR, self.logger)
        
        return user

    ###############################################################
    def get_file(self, host, path, local_path, fname):
        
        self._log(INFO, 'get file from %s / %s / %s (local path %s)' % (host, path, fname, local_path))
        ftp = FTP(host, self.username, self.password)
        try:  # python 2.4 doesn't have try/except/finally
            try:
                ftp.cwd('/%s' % path)
                gfile = open('%s%s' % (local_path, fname), 'wb')
                ftp.retrbinary('RETR %s' % fname, gfile.write)
                gfile.close()
                #result = ResultSet(RESULT_OK, 'got file %s' % fname)
                #result.log(DEBUG, self.logger)
    
            except Exception, e:
                raise IAConnectionError('get file failed: %s on %s- %s' % (fname, host, str(e)))
                """
                result = ResultSet(RESULT_ERROR, 'failed to get "%s".' % fname)
                if hasattr(e, 'code'):
                    result = ResultSet(RESULT_ERROR, 'failed to get "%s" - error code: %s.' % (fname, e.code))
                elif hasattr(e, 'reason'):
                    result = ResultSet(RESULT_ERROR, 'failed to get "%s" - reason: %s.' % (fname, e.reason))
                result.log(ERROR, self.logger)
                """
        finally:
            ftp.quit()
            
        self._log(INFO, 'got file %s' % fname)

    ###############################################################
    def get_http_file(self, path, local_path, fname, min_size=0L):
        """min_size is a hack because archive.org don't return 404 if mp3 file is not found"""
        host = DOWNLOAD_URL
        dl = "%s%s/%s" % (host, path, fname)
        self._log(INFO, 'get_http_file %s' % dl)
        try:
            mp3file = urllib2.urlopen(dl)
            full_fname = '%s%s' % (local_path, fname)
            output = open(full_fname,'wb')
            output.write(mp3file.read())
            output.close()
            file_size = os.path.getsize(full_fname)
            self._log(INFO, 'file size- %s' % str(file_size))
            if file_size <= min_size:
                os.remove(full_fname)
                raise Exception('file too small- probably not found')
        except Exception, e:
            raise IAConnectionError('get_http_file failed: %s - %s' % (dl, str(e)))    
        
    ###############################################################
    def put_file(self, host, path, fname, local_path=None, stream=None):

        self._log(DEBUG, 'put file on %s / %s / %s (local path %s)' % (host, path, fname, local_path))
        ftp = FTP(host, self.username, self.password)
        try:  # python 2.4 doesn't have try/except/finally
            try:
                ftp.cwd('/%s' % path)
                if stream is None:
                    gfile = open('%s%s' % (local_path, fname), 'rb')
                    ftp.storbinary('STOR %s' % fname, gfile)
                    gfile.close()
                else:
                    ftp.storbinary('STOR %s' % fname, stream)
                    
                #result = ResultSet(RESULT_OK, 'put file %s' % fname)
                #result.log(DEBUG, self.logger)
    
            except Exception, e:
                raise IAConnectionError('put file failed: %s on %s- %s' % (fname, host, str(e)))
                """
                result = ResultSet(RESULT_ERROR, 'failed to put "%s".' % fname)
                if hasattr(e, 'code'):
                    result = ResultSet(RESULT_ERROR, 'failed to put "%s" - error code: %s.' % (fname, e.code))
                elif hasattr(e, 'reason'):
                    result = ResultSet(RESULT_ERROR, 'failed to put "%s" - reason: %s.' % (fname, e.reason))
                result.log(ERROR, self.logger)
                """
        finally:
            ftp.quit()
        
        self._log(INFO, 'put file %s' % fname)
        
    ###############################################################
    def set_uploader(self, name):
        if not name:
            self.username = None
            self.password = None
            self.logout()
        elif self.username != name:
            self.username = name
            self.password = self.uploaders[name]
            if self.logged_in():
                self.logout()
                self.login()

    ###############################################################
    def _get_anon(self):
        return self.username is None
    anon = property(_get_anon)

    ###############################################################
    def update_metadata(self, rec_id, metadata, collections={}):
        """
        TODO: setting collections is not working
        """
        from ClientForm import ParseResponse
        
        self._log(DEBUG, 'updating metadata for %s' % rec_id)
        if not self.logged_in():
            raise IAConnectionError('not logged in')

        txheaders = { 'Cookie': self.cookies, }
        txheaders.update(DEF_HEADERS)
        
        # currentFieldNum workaround
        # this hidden field not showing in client form below
        # getting it by reading page and using BeautifulSoup
        # but page is a stream, so has to be re-fetched to read it again below
        
        page = self._get_page('%s?type=audio&edit_item=%s' % (UPDATE_METADATA_URL, rec_id), None, txheaders)
        soup = BeautifulSoup(page)
        try:
            currentFieldNum = int(soup.find(id='currentFieldNum')['value'])
        except TypeError:
            # not found so some problem getting the right page
            raise IAConnectionError('get metadata update page failed (could not find "currentFieldNum"): %s' % rec_id) 
        

        # have to re-fetch page, see note above
        page = self._get_page('%s?type=audio&edit_item=%s' % (UPDATE_METADATA_URL, rec_id), None, txheaders)
        forms = ParseResponse(page, backwards_compat=False)
        form = forms[1]  # search form is first
        control = form.find_control("field_default_collection")
        control.readonly = False
        control = form.find_control("field_default_creator")
        control.readonly = False
        
        # field_default_collection & field_default_creator  in metadata
        
        for attr in metadata.keys():
            #print attr
            try:
                form[attr] = metadata[attr]
            except TypeError:
                raise IAConnectionError('setting metadata key failed: %s' % attr)
            #print form[attr]
        #print form
        # read list of collections from form
        # find value='collection', get name
        #<input readonly="readonly" value="collection" name="field_custom_name_1"/>
        #<input size="45" readonly="readonly" value="raretunes" name="field_custom_value_1"/>
        form_collections = [form.find_control(coll.name.replace('_name_', '_value_')).value for coll in form.controls if coll.value == 'collection']
        form_collections.append(form['field_default_collection'])
        
        #print 'form collections: ', form_collections
        # add missing collections
        rqd_collections = [coll for coll in collections if coll not in form_collections]
        self._log(DEBUG,  'rqd collections: %s' % rqd_collections)
        
        #<input type="text" name="field_custom_name_23" id="field_custom_name_23"/>
        #<input type="text" name="field_custom_value_23" id="field_custom_value_23" size="45"/> 
        
        # THIS DOESN'T WORK- currentFieldNum = form["currentFieldNum"] #.value
        # SEE NOTE ABOVE FOR WORKAROUND
        #print 'currentFieldNum= ', currentFieldNum
        
        for coll in rqd_collections:
            name = 'field_custom_%%s_%d' % currentFieldNum
            coll_name = form.new_control('input', name % 'name', 
                {'id': name % 'name', 'value': 'collection', 'readonly': 'readonly'})
            coll_value = form.new_control('input', name % 'value',
                {'id': name % 'value', 'value': coll, 'readonly': 'readonly'})
            currentFieldNum += 1
        
        form.new_control('hidden', 'currentFieldNum', 
                {'id': 'currentFieldNum', 'value': str(currentFieldNum)})
        #print form
        # form.click() returns a urllib2.Request object
        
        #TODO collection update not working  ??try adding headers etc...
        try:
            url, data, hdrs = form.click_request_data()
        except Exception, e:
            raise Exception('problem submitting metadata form (form.click_request_data()): %s- %s' % (rec_id, str(e))) 
        #req = form.click('submit')
        # add headers, then do below
        #page = urlopen(req).read()
        
        hdrs.append(('Cookie', self.cookies),)
        page = self._get_page(url, data, dict(hdrs))
        #print url, data, hdrs
        
        #parse result for 'Successful!'
        soup = BeautifulSoup(page)
        result = soup.find(text='Successful!')
        self._log(INFO, 'metadata update: %s' % result)
        return result
