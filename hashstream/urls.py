from django.conf.urls import patterns, include, url
from hashstream import views

urlpatterns = patterns('',
	url(r'^(?P<hashtag>\d+)/instagramPush$', views.instagramPushListener),
	url(r'^(?P<hashtag>\d+)$', views.instagramTagStream)
)