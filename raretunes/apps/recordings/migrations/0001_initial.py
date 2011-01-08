# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Artist'
        db.create_table('recordings_artist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=64, unique=True, db_index=True)),
            ('year_of_birth', self.gf('django.db.models.fields.CharField')(max_length=4, blank=True)),
            ('year_of_death', self.gf('django.db.models.fields.CharField')(max_length=4, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('pic', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('tags', self.gf('tagging.fields.TagField')()),
            ('date_entered', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
        ))
        db.send_create_signal('recordings', ['Artist'])

        # Adding model 'Recording'
        db.create_table('recordings_recording', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=240)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=84, unique=True)),
            ('recording_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('tags', self.gf('tagging.fields.TagField')()),
            ('other_keywords', self.gf('django.db.models.fields.CharField')(max_length=84, null=True, blank=True)),
            ('archive', self.gf('django.db.models.fields.CharField')(default='archive.org', max_length=36)),
            ('licence_type', self.gf('django.db.models.fields.CharField')(default='by-nc-sa_2.5_scotland', max_length=36)),
            ('attribution_url', self.gf('django.db.models.fields.URLField')(default='http://raretunes.org', max_length=200, null=True)),
            ('music_img', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('abc', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('date_entered', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
            ('wav_id', self.gf('django.db.models.fields.CharField')(max_length=84, blank=True)),
            ('sound_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('run_time', self.gf('django.db.models.fields.CharField')(max_length=8, null=True, blank=True)),
            ('original_recording_location', self.gf('django.db.models.fields.CharField')(max_length=84, null=True, blank=True)),
            ('original_recording_ownership', self.gf('django.db.models.fields.CharField')(max_length=84, null=True, blank=True)),
            ('original_recording_format', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('record_publisher', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('serial_number', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('matrix_number', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('collector', self.gf('django.db.models.fields.CharField')(max_length=84, null=True, blank=True)),
            ('place_of_recording', self.gf('django.db.models.fields.CharField')(max_length=84, null=True, blank=True)),
            ('geography_of_subject', self.gf('django.db.models.fields.CharField')(max_length=84, null=True, blank=True)),
            ('musical_form', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('opening_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('technical_notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='new', max_length=36, null=True)),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('last_archive_update', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('archive_account', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('IA_id', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('AWS_id', self.gf('django.db.models.fields.CharField')(max_length=84, null=True, blank=True)),
            ('publish_queue_status', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
        ))
        db.send_create_signal('recordings', ['Recording'])

        # Adding M2M table for field performers on 'Recording'
        db.create_table('recordings_recording_performers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('recording', models.ForeignKey(orm['recordings.recording'], null=False)),
            ('artist', models.ForeignKey(orm['recordings.artist'], null=False))
        ))
        db.create_unique('recordings_recording_performers', ['recording_id', 'artist_id'])

        # Adding M2M table for field composers on 'Recording'
        db.create_table('recordings_recording_composers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('recording', models.ForeignKey(orm['recordings.recording'], null=False)),
            ('artist', models.ForeignKey(orm['recordings.artist'], null=False))
        ))
        db.create_unique('recordings_recording_composers', ['recording_id', 'artist_id'])


    def backwards(self, orm):
        
        # Deleting model 'Artist'
        db.delete_table('recordings_artist')

        # Deleting model 'Recording'
        db.delete_table('recordings_recording')

        # Removing M2M table for field performers on 'Recording'
        db.delete_table('recordings_recording_performers')

        # Removing M2M table for field composers on 'Recording'
        db.delete_table('recordings_recording_composers')


    models = {
        'recordings.artist': {
            'Meta': {'ordering': "['last_name']", 'object_name': 'Artist'},
            'date_entered': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'pic': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '64', 'unique': 'True', 'db_index': 'True'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'year_of_birth': ('django.db.models.fields.CharField', [], {'max_length': '4', 'blank': 'True'}),
            'year_of_death': ('django.db.models.fields.CharField', [], {'max_length': '4', 'blank': 'True'})
        },
        'recordings.recording': {
            'AWS_id': ('django.db.models.fields.CharField', [], {'max_length': '84', 'null': 'True', 'blank': 'True'}),
            'IA_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'Meta': {'ordering': "['title']", 'object_name': 'Recording'},
            'abc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'archive': ('django.db.models.fields.CharField', [], {'default': "'archive.org'", 'max_length': '36'}),
            'archive_account': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'attribution_url': ('django.db.models.fields.URLField', [], {'default': "'http://raretunes.org'", 'max_length': '200', 'null': 'True'}),
            'collector': ('django.db.models.fields.CharField', [], {'max_length': '84', 'null': 'True', 'blank': 'True'}),
            'composers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'composers'", 'blank': 'True', 'null': 'True', 'to': "orm['recordings.Artist']"}),
            'date_entered': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'geography_of_subject': ('django.db.models.fields.CharField', [], {'max_length': '84', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'last_archive_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'licence_type': ('django.db.models.fields.CharField', [], {'default': "'by-nc-sa_2.5_scotland'", 'max_length': '36'}),
            'matrix_number': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'music_img': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'musical_form': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'opening_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'original_recording_format': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'original_recording_location': ('django.db.models.fields.CharField', [], {'max_length': '84', 'null': 'True', 'blank': 'True'}),
            'original_recording_ownership': ('django.db.models.fields.CharField', [], {'max_length': '84', 'null': 'True', 'blank': 'True'}),
            'other_keywords': ('django.db.models.fields.CharField', [], {'max_length': '84', 'null': 'True', 'blank': 'True'}),
            'performers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'performers'", 'blank': 'True', 'null': 'True', 'to': "orm['recordings.Artist']"}),
            'place_of_recording': ('django.db.models.fields.CharField', [], {'max_length': '84', 'null': 'True', 'blank': 'True'}),
            'publish_queue_status': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'record_publisher': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'recording_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'run_time': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'serial_number': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '84', 'unique': 'True'}),
            'sound_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '36', 'null': 'True'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'technical_notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '240'}),
            'wav_id': ('django.db.models.fields.CharField', [], {'max_length': '84', 'blank': 'True'})
        }
    }

    complete_apps = ['recordings']
