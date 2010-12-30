import urllib2
from urlparse import urlparse
import re
import sys, os

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup, SoupStrainer
from ftplib import FTP

os.environ['DJANGO_SETTINGS_MODULE'] ='raretunes.settings'
from django.core.management import setup_environ
from raretunes import settings

setup_environ(settings)

import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    #filename= '%s%s' % (TEMP_ROOT, 'publish_log.txt') ,
                    #filemode='a'
                    )
conn_logger = logging.getLogger()


conn_logger.debug('--------------------')
conn_logger.debug('test_code.py running')

from iaconnection import IAConnection, IAConnectionError, RESULT_OK
from recordings.models import Recording
from recordings.ia_views import make_metadata

REC_URL = 'http://www.archive.org/details/%s'
CHECKOUT_URL = 'http://www.archive.org/checkout.php?identifier='

if os.path.exists('/Users/derek/temp/'):
    MP3_TEMP_PATH = '/Users/derek/temp/'
elif os.path.exists('/tmp/web/mp3/'):
    MP3_TEMP_PATH = '/tmp/web/mp3/'
else:
    MP3_TEMP_PATH = 'd:/temp/'

test_trax = (
    ('raretunes__an_thou_were_my_ain_thing', 'A very old Scottish song tune. The song and tune were re-used by Robert Burns.'),
    #('DonaldWasAPiper', ''),
    #('EarlOfDalhousie', ''),
    #('DashingWhiteSergeant', ''),
    )
DEF_IA_UPLOADER = 'archive@ganzie.com'
IA_UPLOADERS = {
        DEF_IA_UPLOADER: 'vienna' ,
        'raretunes@ganzie.com': 'morino' ,
        'eydmann@blueyonder.co.uk': 'chanter'
    }
AWS_U = '0DK12GK23780YNSD6VG2'
AWS_K = 'JbD5hw4A+CuqyA+3V0CvDBZIFMAaPmeXO74Yv64E'

import eyeD3
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message

Q_RT_PUBLISH = 'dev_mac_publish'
Q_RT_CHECKIN = 'dev_mac_checkin'

###############################################################
def queue(q_name, msg):

    conn_logger.debug('queue')
    sqs_conn = SQSConnection(AWS_U, AWS_K)
    q = sqs_conn.create_queue(q_name)
    m = Message()
    m.set_body(msg)
    rs = q.write(m)
    
    conn_logger.debug('put "%s" to %s queue: ' % (msg, q_name))

###############################################################
def dequeue(q_name, func, conn=None):

    conn_logger.debug('dequeuing %s' % q_name)
    sqs_conn = SQSConnection(AWS_U, AWS_K)
    q = sqs_conn.create_queue(q_name)
    #q.clear()
    rs = q.get_messages(5)
    if len(rs) == 0:
        conn_logger.info('%s queue is empty' % q_name)
    else:    
        for m in rs:
            msg = m.get_body()
            if func(msg, conn):
                q.delete_message(m)
                conn_logger.info('dequeue done: %s from %s' % (msg, q_name))

    #conn_logger.debug('dequeue done')

###############################################################
def put_to_S3(rec):

    conn = S3Connection(AWS_U, AWS_K)
    conn_logger.debug('S3 connection')
    b = conn.create_bucket(AWS_BUCKET)
    conn_logger.debug('got bucket')
    k = Key(b)
    conn_logger.debug('got key')
    fname = '%s_vbr.mp3' % rec.source_id
    k.key = fname
    local_path = '%s' % (MP3_TEMP_PATH)
    try:
        k.set_contents_from_filename('%s%s' % (local_path, fname))
        conn_logger.info('file put: %s' % fname)
        k.set_acl('public-read')
        conn_logger.debug('acl set')
    except IOError, e:
        conn_logger.error('put to S3 failed: %s - %s' % (fname, str(e)))

###############################################################
def tag_mp3(fname, rec, comment):
    conn_logger.debug('tag mp3 %s' % fname)
    
    tag = eyeD3.Tag()
    tag.link(fname)
    tag.setTitle(rec.title)
    tag.setArtist(rec.performer_names)
    tag.addComment(comment)
    tag.update()

    conn_logger.info('tagged mp3 "%s"' % fname)
    return True
    
###############################################################
def publish(rec, conn):

    if not isinstance(rec, Recording):
        rec = Recording.objects.get(pk=rec)
    if not rec.archive_account:
        rec.archive_account = conn.get_uploader(rec.slug)
        rec.save()
    conn.set_uploader(rec.archive_account)
    try:
        conn.login()
        host_url = conn.checkout(rec.slug)
        host = host_url.split('@')[1].split('/')[0]
        fname = '%s_vbr.mp3' % rec.source_id
        #local_path = '%s%s' % (TEMP_ROOT, 'mp3/')
        fname_exists = os.path.exists('%s%s' % (MP3_TEMP_PATH, fname))
        path = rec.slug
        if not fname_exists:
            conn.get_file(host, path, MP3_TEMP_PATH, fname)
        tag_mp3('%s%s' % (MP3_TEMP_PATH, fname), rec, 'See http://raretunes.org%s for information and copyright' % rec.get_absolute_url())
        conn.put_file(host, path, fname, local_path=MP3_TEMP_PATH)
        queue(Q_RT_CHECKIN, str(rec.id))
        os.remove('%s%s' % (MP3_TEMP_PATH, fname))
        if rec.status != 'withdrawn':
            rec.status = 'published'
        rec.archive_account = conn.username
        rec.AWS_id = fname
        rec.save()
        return True
        
    except IAConnectionError, e:
        conn_logger.error(e)
        return False

###############################################################
def process_publish(conn):
    dequeue(Q_RT_CHECKIN, publish, conn)

###############################################################
def _checkin_message(rec_id, conn):
    rec = Recording.objects.get(pk=rec_id)
    conn_logger.debug('checkin in %s' % rec.slug)
    conn.set_uploader(rec.archive_account)
    conn.checkin(rec.slug)
    return True

###############################################################
def process_checkin(conn):
    dequeue(Q_RT_CHECKIN, _checkin_message, conn)

###############################################################
def process_queues(conn):
    dequeue(Q_RT_CHECKIN, _checkin_message, conn)
    dequeue(Q_RT_PUBLISH, publish, conn)


###############################################################
'''
class CallBacker(object):
    def __init__(self):
        pass
    def increment(self, status): pass
    def reset(self): pass
    def finish(self): pass
    def reset(self,steps=1,filename=None,status=''):
        pass
    def __call__(self, bytes=1): pass

cb_dummy = CallBacker()
cb_dummy.increment('')
cb_dummy.reset(steps=10)
cb_dummy.finish()

from pyarchive.submission import ArchiveItem, UploadApplication
'''
ia_conn = IAConnection('archive@ganzie.com', 'vienna', conn_logger)
ia_conn.uploaders = IA_UPLOADERS
ia_conn.login()


i= 155
rec = Recording.objects.get(pk=i)
print rec.title
# print rec.create_metadata()

'''
ia_conn.update_metadata(rec.slug, make_metadata(rec), settings.DEF_COLLECTIONS)


uploader = UploadApplication('RareUploader', '0.1')


from django.db.models import signals
from django.dispatch import dispatcher
from recordings.ia_views import queue_metadata_update

dispatcher.connect(queue_metadata_update, signal=signals.post_save, sender=Recording)

i= 100
rec = Recording.objects.get(pk=i)
rec.save()


print rec.make_IA_archive_item().metaxml().getvalue()


FILE_CLAIM = '2008 RareTunes. Licensed to the public under %s verify at http://www.archive.org/details/%s'
LIC_URL = 'http://creativecommons.org/licenses/by-nc-sa/2.5/scotland/'
t = ArchiveItem(uploader, LIC_URL)
t.title = 'My A Tone'
t.identifier = 'raretunes_test_0001'
t.collection = 'test_collection'
t.mediatype = 'audio'
t.addFile('D:\\temp\\a tone.wav', 'original', 'WAVE', FILE_CLAIM % (LIC_URL, t.identifier))
t.submit( DEF_IA_UPLOADER, IA_UPLOADERS[DEF_IA_UPLOADER], server=None, callback=cb_dummy)

ia_conn = IAConnection('archive@ganzie.com', 'vienna', conn_logger)
ia_conn.uploaders = IA_UPLOADERS
ia_conn.login()


i= 100
rec = Recording.objects.get(pk=i)

#queue(Q_RT_PUBLISH, str(i))

publish(rec, ia_conn)
put_to_S3(rec)
for i in range(1, 6):

#for i in range(1, 11):
for r in Recording.objects.filter(status='published', AWS_id__isnull=True):
    print r.slug
    queue('ia_publish', str(r.id))
#process_queues(ia_conn)
'''

conn_logger.debug('---- finished ------')
conn_logger.debug('')

"""
###############################################################
def update_metadata(track, url, soup):

    descr_tag = soup.find(name='description')
    descr_tag.string.replaceWith('%s \n(see raretunes.org)' % descr_tag.string)
    print soup.prettify()
    outfile = open('%s%s' % (TEMP_ROOT, 'temp.xml'), 'w')
    outfile.write(soup.prettify())
    outfile.close()
    
    user = soup.find(name='uploader').string
        
    print 'opening %s' % url
    result = urlparse(url)
    print result.hostname
    print result.path
    ftp = FTP(result.hostname)
    try:
        ##  login not working with user- anon OK
        ##  ?? needs a 'checkout' done first
        print ftp.login()  #(user, uploaders[user])
        #ftp.cwd(result.path)
        #ftp.retrlines('LIST')
        
        
        #ftp.retrlines('RETR %s_meta.xml' % track, handle_line)  
        
    finally:
        ftp.quit()
"""

