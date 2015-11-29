import sys
import re

from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

admin.autodiscover()

from core.views import IndexView, MatchesView

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', IndexView.as_view(), name="index"),
    url(r'^api/league/(?P<league_level>\w+)/matches/$', MatchesView.as_view())
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# http://stackoverflow.com/questions/8258417
if 'test' in sys.argv:
    static_url = re.escape(settings.STATIC_URL.lstrip('/'))
    urlpatterns += patterns(
        '',
        url(
            r'^%s(?P<path>.*)$' % static_url,
            'django.views.static.serve',
            {
                'document_root': settings.STATIC_ROOT,
            }
        ),
    )

