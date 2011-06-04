from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext 


def uploads_waiting(request):

    from boto.s3.connection import S3Connection
    from boto.s3.key import Key
    import sys

    conn = S3Connection(settings.AWS_U, settings.AWS_K)
    bucket = conn.get_bucket(settings.AWS_BUCKET)

    objects = [('http://%s/%s' % (settings.AWS_BUCKET, o.name), o.name[len(settings.AWS_UPLOADS)+1:]) for o in bucket.list(settings.AWS_UPLOADS)]

    # for key in rs:
    #    print key.name

    return render_to_response('admin/recordings/uploads_waiting.html',
                              { 'objects': objects, },
                              context_instance=RequestContext(request))

