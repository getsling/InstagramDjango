from django.conf.urls import patterns, include, url
from django.contrib import admin
from streamer import views

admin.autodiscover()

urlpatterns = patterns('',
	# Uncomment the next line to enable the admin:
	url(r'^admin/', include(admin.site.urls)),
	url(r'^instagramPush/(.*)$', views.instagramPushListener),
	url(r'^testApi/', views.testApi),
	url(r'^tag/(\w+)$', views.instagramEndpoint),
	url(r'^testtag/(\w+)$', views.instagramTagStream)
)
