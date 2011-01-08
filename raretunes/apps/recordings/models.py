""" raretunes.recordings.models.py

"""

from django.db import models
from django.conf import settings

from tagging.fields import TagField
#from shared_apps.recordings.ia_views import queue_metadata_update
import datetime

from pyarchive.submission import ArchiveItem, UploadApplication

uploader = UploadApplication('RareUploader', '0.1')

RECORDING_STATUS = (('new', 'new'), ('published', 'published'), ('withdrawn', 'withdrawn'), )
RECORDING_STATUS_DEFAULT = 'new'
RECORDING_STATUS_PUBLISHED = 'published'


class ArtistsWithRecordingsManager(models.Manager):
    def get_query_set(self):
        return super(ArtistsWithRecordingsManager, self).get_query_set().filter(performers__isnull=False).distinct()

###############################################################
class Artist(models.Model):
###############################################################
    
    first_name = models.CharField(max_length=64, blank=True)
    last_name  = models.CharField(max_length=64, blank=False)
    slug = models.SlugField(
        max_length=64,
        unique=True
    )
    year_of_birth = models.CharField(max_length=4, blank=True)
    year_of_death = models.CharField(max_length=4, blank=True)
    url = models.URLField(blank=True)
    note = models.TextField(blank=True)
    pic = models.ImageField(upload_to="artists", null=True, blank=True)
    pic_credit = models.TextField(null=True, blank=True)
    additional_info = models.TextField(null=True, blank=True)
    tags = TagField()
    date_entered = models.DateField(default=datetime.date.today)

    objects = models.Manager()
    with_recordings = ArtistsWithRecordingsManager()

    class Admin:
        pass
    
    class Meta:
        ordering = ['last_name']

    def __unicode__(self):
        return "%s, %s" % (self.last_name, self.first_name)
    
    def get_absolute_url(self):
        return "/artists/%s/" % self.slug

    def _get_full_name(self):
        return '%s %s' % (self.first_name, self.last_name)
    full_name = property(_get_full_name)

    def _get_published_recordings(self):
        return self.performers.filter(status=RECORDING_STATUS_PUBLISHED)
    published_recordings = property(_get_published_recordings)
        
        
# from shared_apps.fulltext_search.models import SearchManager

class PublishedRecordingManager(models.Manager):
    def get_query_set(self):
        return super(PublishedRecordingManager, self).get_query_set().filter(status='published')

ARCHIVE_CHOICES = (('archive.org', 'archive.org'),)
ARCHIVE_DEFAULT = 'archive.org'


SQS_STATUS = (('xxx', 'xxx'),)

ARCHIVE_METADATA = [
    'original_recording_location', 'original_recording_ownership', 'original_recording_format',
    'record_publisher', 'serial_number', 'matrix_number', 'collector',
    'place_of_recording', 'geography_of_subject', 'musical_form', 'language',
    'opening_text', 'technical_notes',
    ]


###############################################################
class Recording(models.Model):
###############################################################
    
    title = models.CharField(max_length=240)
    slug = models.CharField(
        max_length=84,
        unique=True
    )
    recording_date = models.DateField(null=True, blank=True)
    performers = models.ManyToManyField(Artist, related_name='performers', null=True, blank=True)
    composers = models.ManyToManyField(Artist, related_name='composers', null=True, blank=True)
    #published = models.BooleanField(default=True)
    note = models.TextField(blank=True, help_text='a link to RareTunes will be added for Archive.org') 
    additional_info = models.TextField(null=True, blank=True)
    tags = TagField()
    other_keywords = models.CharField(max_length=84, null=True, blank=True, help_text='comma separated')
    archive = models.CharField(max_length=36, choices=ARCHIVE_CHOICES, default=ARCHIVE_DEFAULT)
    licence_type = models.CharField(
        max_length=36, choices=settings.LICENCE_TYPES, default=settings.LICENCE_TYPES_DEFAULT)
    attribution_url=models.URLField(null=True, default='http://raretunes.org')
    music_img = models.ImageField(upload_to="dots", null=True, blank=True)
    abc = models.TextField(null=True, blank=True)
    
    date_entered = models.DateField(default=datetime.date.today)
    wav_id = models.CharField(
        'wav filename',
        help_text='ONLY EDIT THIS FIELD IF SOUND FILE IS NOT UPLOADED FROM RARETUNES',
        max_length=84,
        blank=True
    )
    sound_file = models.FileField(upload_to='recordings', null=True, blank=True)
    run_time = models.CharField(max_length=8, null=True, blank=True, help_text='mm:ss')
    
    #archive metadata
    original_recording_location = models.CharField(max_length=84, null=True, blank=True)
    original_recording_ownership = models.CharField(max_length=84, null=True, blank=True)
    original_recording_format = models.CharField(max_length=36, null=True, blank=True)
    record_publisher = models.CharField(max_length=36, null=True, blank=True)
    serial_number = models.CharField(max_length=36, null=True, blank=True)
    matrix_number = models.CharField(max_length=36, null=True, blank=True)
    collector = models.CharField(max_length=84, null=True, blank=True, help_text='if field recording')
    place_of_recording = models.CharField(max_length=84, null=True, blank=True)
    geography_of_subject = models.CharField(max_length=84, null=True, blank=True)
    musical_form = models.CharField(max_length=36, null=True, blank=True)
    language = models.CharField(max_length=36, null=True, blank=True)
    opening_text = models.TextField(null=True, blank=True, help_text='as a reference')
    technical_notes = models.TextField(null=True, blank=True)

    # new stuff
    status = models.CharField(max_length=36, choices=RECORDING_STATUS, default=RECORDING_STATUS_DEFAULT, null=True )
    last_update = models.DateTimeField(null=True, blank=True)
    last_archive_update = models.DateTimeField(null=True, blank=True)
    archive_account = models.CharField(max_length=64, null=True, blank=True)
    IA_id = models.CharField(max_length=100, null=True, blank=True)
    AWS_id = models.CharField(max_length=84, null=True, blank=True)
    publish_queue_status = models.CharField(max_length=36, choices=SQS_STATUS, blank=True, null=True )
    
    objects = models.Manager()
    published_recordings = PublishedRecordingManager()
    # Use a SearchManager for retrieving objects,
    # and tell it which fields to search. 
    # searcher = SearchManager(('title', 'note'))
    
    class Admin:
        pass

    class Meta:
        ordering = ['title']

    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        return "/recordings/%s/" % self.slug

    def _get_archive_name(self):
        return self.IA_id #slug #.replace('-', '_')
    archive_name = property(_get_archive_name)

    def _get_creator(self):
        return ','.join([p.full_name for p in self.performers.all()])
    creator = property(_get_creator)
    
    def _get_source_id(self):
        return self.wav_id.split('.')[0]
    source_id = property(_get_source_id)
    
    def _get_play_url(self):
        if self.AWS_id:
            return 'http://media.raretunes.org/%s' % ( self.AWS_id)
            
        elif self.archive == 'archive.org':
            if self.wav_id.rfind('.') == -1:
                ext = '.mp3'
            else:
                ext = ''
            return 'http://www.archive.org/download/%s/%s%s' % ( self.archive_name, self.wav_id, ext)
        else:
            return 'unknown archive'
    play_url = property(_get_play_url)
    
    def _get_published(self):
        return self.status == RECORDING_STATUS_PUBLISHED
    published = property(_get_published)
    
    def _get_performers(self):
        return ', '.join([artist.full_name for artist in self.performers.all()])
    performer_names = property(_get_performers)
    
    ### in ia_views.py - dispatcher.connect(queue_metadata_update, signal=signals.post_save, sender=Recording)
      
    def save(self, *args, **kwargs):
        if self.pk is None:
            pass
        #raise Exception('not gonna do it')
        last_update = datetime.datetime.now()
        super(Recording, self).save(*args, **kwargs)

    def get_licence_url(self):
        return 'http://creativecommons.org/licenses/%s/' % self.licence_type.replace('_', '/')

    def make_subjects(self):
        _subjects = '%s; %s' % ('; '.join(list(self.tags.all())), settings.DEF_TAGS)
        if self.other_keywords:
            others = '; '.join([kw.strip() for kw in self.other_keywords.split(',')])
            if others:
                _subjects = '%s; %s' % (_subjects, others)
        return _subjects

    def create_metadata(self):
        result = {
            'collection': settings.DEF_COLLECTIONS,
            'description': '%s\n%s' % (self.note, settings.STANDARD_FOOTER % self.slug),
            'creator': self.performer_names,
            'date': self.recording_date and self.recording_date.strftime('%Y-%m-%d'),
            'subjects': self.make_subjects().replace('; ',','),
            'taper': self.collector,
            'runtime': self.run_time,
            }
        # build metadata from recording
        for m in ARCHIVE_METADATA:
            md = getattr(self, m, None)
            if md:
                result[m] = md
        
        return result
