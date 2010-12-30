""" shared_apps.recordings.ia_views

"""
from django.conf import settings
from django.db.models import signals
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import Context, loader
from recordings.models import Recording

import urllib2
from urlparse import urlparse
import re
import sys, os

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup, SoupStrainer
from ftplib import FTP
import eyeD3
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message
from pyarchive.submission import ArchiveItem, UploadApplication

from iaconnection import IAConnection, IAConnectionError, RESULT_OK
from recordings.models import Recording

from settings import IA_UPLOADERS, DEF_IA_UPLOADER, Q_RT_CREATE, Q_RT_PUBLISH, Q_RT_CHECKIN, Q_RT_UPDATE_METADATA
from settings import MP3_TEMP_PATH, AWS_U, AWS_K, AWS_BUCKET

import logging
#conn_logger = None
conn_logger = logging.getLogger()


###############################################################
class CallBacker(object):
    def __init__(self):
        pass
    def increment(self, status): pass
    def reset(self): pass
    def finish(self): pass
    def reset(self,steps=1,filename=None,status=''):
        pass
    def __call__(self, bytes=1): pass


###############################################################
def queue(q_name, msg):

    conn_logger.debug('queue')
    sqs_conn = SQSConnection(AWS_U, AWS_K)
    q = sqs_conn.create_queue(q_name)
    m = Message()
    m.set_body(msg)
    rs = q.write(m)
    
    conn_logger.info('put "%s" to %s queue: ' % (msg, q_name))

###############################################################
def dequeue(q_name, func, conn=None):

    conn_logger.info('dequeuing %s' % q_name)
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
def make_IA_archive_item(rec, metadata=None):
    
    conn_logger.info('make_IA_archive_item: %s' % rec.slug)
    if not rec.sound_file.name:
        raise IAConnectionError('no sound file for #%s %s' % (rec.id, rec.slug))
    full_fname = '%s/%s' % (settings.MEDIA_ROOT, rec.sound_file.name)     # rec.get_sound_file_filename()
    if not os.path.exists(full_fname):
        raise IAConnectionError('sound file not found for #%s %s: %s' % (rec.id, rec.slug, full_fname))

    uploader = UploadApplication('RareUploader', '0.1')
    item = ArchiveItem(uploader, rec.get_licence_url())
    item.title = rec.title
    item.identifier = settings.IA_ID % (rec.id, rec.slug)
    item.collection = settings.DEF_COLLECTIONS[0]
    item.mediatype = 'audio'
    if not metadata:
        metadata = rec.create_metadata()
    item.metadata.update(metadata)
    item.addFile(full_fname, 'original', 'WAVE', settings.FILE_CLAIM % (rec.get_licence_url(), item.identifier))

    return item

###############################################################
def _create_recording(rec, conn):
    try:
        if not isinstance(rec, Recording):
            try: 
                rec = Recording.objects.get(pk=rec)
            except Recording.DoesNotExist:
                conn_logger.error('create_recording failed (recording does not exist): %s ' % rec)
                return True
        # check recording is valid:
        if rec.status != 'new':
            conn_logger.error('create_recording failed (status not "new"): %s ' % rec.slug)
            return True
        if rec.sound_file is None:
            if not (rec.wav_id and rec.slug):
                conn_logger.error('create_recording failed (no sound file and no archive ID/wav ID): %s ' % rec.slug)
                return False
            else:
                # no sound file, but archive id (slug) and wav_id provided
                # so not RareTunes hosted
                return True # allow dequeue
        t = make_IA_archive_item(rec)
        try:
            t.submit(DEF_IA_UPLOADER, IA_UPLOADERS[DEF_IA_UPLOADER], server=None, callback=CallBacker())
        except Exception, e:
            conn_logger.error('submit new recording failed: %s - %s' % (rec.slug, str(e)))
            raise IAConnectionError(e)

        conn_logger.info('created recording : %s ' % rec.slug)
        rec.IA_id = t.identifier
        rec.wav_id = rec.sound_file.name.split('/')[1]
        rec.save()
        queue(Q_RT_PUBLISH, str(rec.id))
    except IAConnectionError, e:
        conn_logger.error(e)
        return False
    
    return True

###############################################################
def put_to_S3(fname):

    conn = S3Connection(AWS_U, AWS_K)
    conn_logger.info('S3 connection')
    b = conn.create_bucket(AWS_BUCKET)
    conn_logger.debug('got bucket')
    k = Key(b)
    conn_logger.debug('got key')
    #fname = '%s_vbr.mp3' % rec.source_id
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
    conn_logger.info('tag mp3 %s' % fname)
    try:
        tag = eyeD3.Tag()
        tag.link(fname)
        tag.remove(eyeD3.ID3_ANY_VERSION)
        #tag.link(fname, eyeD3.ID3_V2)
        title = rec.title.encode('iso-8859-1', 'ignore')
        tag.setTitle(title)
        tag.setArtist(rec.performer_names)
        tag.addComment(comment)
        tag.update()
    except (ValueError, eyeD3.TagException), e:
        conn_logger.error('tag_mp3 failed: %s - %s' % (fname, str(e)))
        #raise IAConnectionError('tag_mp3 failed')
        
    conn_logger.info('tagged mp3 "%s"' % fname)
    return True
    
###############################################################
def publish(rec, conn):

    if not isinstance(rec, Recording):
        rec = Recording.objects.get(pk=rec)
    try:
        if not rec.archive_account:
            rec.archive_account = conn.get_uploader(rec.IA_id)
            rec.save()
        # if unknown uploader:  return True -> dequeue and leave
        if rec.archive_account is None:
            conn_logger.info('unknown archive account- %s  not published' % rec.IA_id)
            if rec.status != 'withdrawn':
                rec.status = 'published'
            return True
        conn.set_uploader(rec.archive_account)
        conn.login()
        # host_url = conn.checkout(rec.IA_id)
        # eg http://ia341316.us.archive.org/edit.php?identifier=raretunes_332_raglan-road
        # host = host_url.split('//')[1].split('/')[0]
        
        # REMOVED vbr now for archive.org
        # fname = '%s_vbr.mp3' % rec.source_id
        
        fname = '%s.mp3' % rec.source_id
        full_fname = '%s%s' % (MP3_TEMP_PATH, fname)
        fname_exists = os.path.exists(full_fname)
        #if fname_exists and os.path.getsize(full_fname) == 0L:
        #    os.remove(full_fname)
        #    fname_exists = False
        path = rec.IA_id
        if (not fname_exists) or os.path.getsize(full_fname) == 0L:
            # conn.get_file(host, path, MP3_TEMP_PATH, fname)
            conn.get_http_file(path, MP3_TEMP_PATH, fname, 5000L)
            # http://www.archive.org/download/raretunes_332_raglan-road/raretunesandrewraglan_vbr.mp3
            
        # conn_logger.info('mp3 file size- %s' % str(os.path.getsize(full_fname)))
        
        tag_mp3(full_fname, rec, 'See http://raretunes.org%s for information and copyright' % rec.get_absolute_url())
        # conn.put_file(host, path, fname, local_path=MP3_TEMP_PATH)
        # queue(Q_RT_CHECKIN, str(rec.id))
        put_to_S3(fname)
        os.remove(full_fname)
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
    conn_logger.info('checkin in %s' % rec.IA_id)
    conn.set_uploader(rec.archive_account)
    conn.checkin(rec.IA_id)
    return True

###############################################################
def process_checkin(conn):
    dequeue(Q_RT_CHECKIN, _checkin_message, conn)


###############################################################
def queue_metadata_update(sender, instance, created, **kwargs):
    
    if created:
        queue(Q_RT_CREATE, str(instance.id))
    elif instance.status != 'new': # not published yet
        queue(Q_RT_UPDATE_METADATA, str(instance.id))

signals.post_save.connect(queue_metadata_update, sender=Recording)

###############################################################
def make_metadata(rec):

    result = {

        #'currentFieldNum': ,
        #'edit_item': self.IA_id,
        #'field_custom_name_1': 'resource',
        #'field_custom_value_1': 'audio',
        #'field_custom_name_2': 'collection',  #TODO fix collections
        #'field_custom_value_2': 'audio_music',
        #'field_custom_name_3': 'collection',
        #'field_custom_value_3': '78rpm',
        #'field_default_addeddate': ,
        #'field_default_adder': ,
        'field_default_collection': settings.DEF_COLLECTIONS[0],
        'field_default_creator': rec.performer_names,
        #'field_default_date': ,
        'field_default_description': '%s\n%s' % (rec.note, settings.STANDARD_FOOTER % rec.slug),
        #'field_default_hidden': ,
        #'field_default_identifier': self.slug,
        #'field_default_licenseurl': self.get_licence_url,
        #'field_default_mediatype': 'audio',
        #'field_default_noindex': ,
        #'field_default_notes': ,
        #'field_default_pick': ,
        #'field_default_public': ,
        #'field_default_publicdate': ,
        'field_default_runtime': rec.run_time,
        'field_default_source': rec.collector,
        'field_default_subject': rec.make_subjects(),
        'field_default_taper': rec.collector,
        'field_default_title': rec.title,
        #'field_default_updatedate': ,
        #'field_default_updater': ,
        #'field_default_uploader': ,
        #'filesxml_3_album': ,
        #'filesxml_3_creator': ,
        #'filesxml_3_filename': ,
        #'filesxml_3_format': ,
        #'filesxml_3_title': ,
        #'filesxml_3_track': ,
        #'newccdeed': ,
        #'newccimage': ,
        #'newcclicense': ,
        #'newccname': ,
        #'retaincclicense': 1,
        #'rules': ,
        #'submit': 'Submit',
        #'type': 'audio',
        }
    
    return result

###############################################################
def update_metadata(rec, conn):
    """
    returns True if processing not needed again- to allow dequeuing
    """
    #return True
    if not isinstance(rec, Recording):
        rec = Recording.objects.get(pk=rec)
    conn_logger.info('update metadata %s' % rec.slug)
    try:
        if not rec.archive_account:
            rec.archive_account = conn.get_uploader(rec.IA_id)
            if rec.archive_account is not None:
                rec.save()
        # if unknown uploader:  return True -> dequeue and leave
        if rec.archive_account is None:
            conn_logger.info('unknown archive account- %s  not processed' % rec.IA_id)
            return True
        conn.set_uploader(rec.archive_account)

        conn.login()
        conn.update_metadata(rec.IA_id, make_metadata(rec), settings.DEF_COLLECTIONS)
        return True
        
    except IAConnectionError, e:
        conn_logger.error(e)
        return False
    
###############################################################
def process_queues(request):
    
    if settings.IA_DEBUG:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(level=log_level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename= '%s%s' % (settings.LOG_ROOT, 'publish_log.txt') ,
                        filemode='a'
                        )
    conn_logger.info('---- starting process_queues ----')
    
    ia_conn = IAConnection(settings.DEF_IA_UPLOADER, settings.IA_UPLOADERS[settings.DEF_IA_UPLOADER], conn_logger)
    ia_conn.uploaders = settings.IA_UPLOADERS
    ia_conn.login()
    
    dequeue(Q_RT_CREATE, _create_recording, ia_conn)
    dequeue(Q_RT_CHECKIN, _checkin_message, ia_conn)
    dequeue(Q_RT_PUBLISH, publish, ia_conn)
    dequeue(Q_RT_UPDATE_METADATA, update_metadata, ia_conn)
    
    conn_logger.info('---- ended process_queues ----')
    conn_logger.info('------------------------------')

    return HttpResponse('OK') #, mimetype="text")

