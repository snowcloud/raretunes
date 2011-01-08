# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'CollectionItem'
        db.create_table('recordings_collectionitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['recordings.Collection'])),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['recordings.Recording'])),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('recordings', ['CollectionItem'])

        # Adding model 'Collection'
        db.create_table('recordings_collection', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=240)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=84, unique=True)),
            ('note', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('pic', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('pic_credit', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('additional_info', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('tags', self.gf('tagging.fields.TagField')()),
            ('status', self.gf('django.db.models.fields.CharField')(default='new', max_length=36)),
            ('date_entered', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
        ))
        db.send_create_signal('recordings', ['Collection'])


    def backwards(self, orm):
        
        # Deleting model 'CollectionItem'
        db.delete_table('recordings_collectionitem')

        # Deleting model 'Collection'
        db.delete_table('recordings_collection')


    models = {
        'recordings.artist': {
            'Meta': {'ordering': "['last_name']", 'object_name': 'Artist'},
            'additional_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_entered': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'pic': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'pic_credit': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '64', 'unique': 'True', 'db_index': 'True'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'year_of_birth': ('django.db.models.fields.CharField', [], {'max_length': '4', 'blank': 'True'}),
            'year_of_death': ('django.db.models.fields.CharField', [], {'max_length': '4', 'blank': 'True'})
        },
        'recordings.collection': {
            'Meta': {'object_name': 'Collection'},
            'additional_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_entered': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['recordings.Recording']", 'null': 'True', 'symmetrical': 'False', 'through': "orm['recordings.CollectionItem']", 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'pic': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'pic_credit': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '84', 'unique': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '36'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '240'})
        },
        'recordings.collectionitem': {
            'Meta': {'object_name': 'CollectionItem'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['recordings.Collection']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['recordings.Recording']"})
        },
        'recordings.recording': {
            'AWS_id': ('django.db.models.fields.CharField', [], {'max_length': '84', 'null': 'True', 'blank': 'True'}),
            'IA_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'Meta': {'ordering': "['title']", 'object_name': 'Recording'},
            'abc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'additional_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
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
