from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'rare', 'rarefm_urls', name='rarefm'),
    host(r'^recordings/', 'urls', name='raretunes'),
)