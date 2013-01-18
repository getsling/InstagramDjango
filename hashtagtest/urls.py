from django.conf.urls import patterns, include, url
from django.contrib import admin
from hashstream import views

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hashtagtest.views.home', name='home'),
    # url(r'^hashtagtest/', include('hashtagtest.foo.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
	url(r'^(\w+)/instagramPush$', views.instagramPushListener),
	url(r'^(\w+)$', views.instagramTagStream)
)
