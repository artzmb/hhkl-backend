import sys
import re

from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
admin.autodiscover()

from solid_i18n.urls import solid_i18n_patterns

from core.views import IndexView

urlpatterns = patterns(
    '',
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^admin/', include(admin.site.urls)),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += solid_i18n_patterns(
    '',
    url(r'^$', IndexView.as_view(), name="index"),
)

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

