from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'interface_screen.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^plates/', include('plates.urls', namespace = "plates")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'plates/login.html'}, name='login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'plates/login.html'}, name='logout')
)
