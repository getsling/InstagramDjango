from django.http import HttpResponse
from instagram.client import InstagramAPI
from instagram import subscriptions
from models import Subscription
from models import InstagramImage
from django.db.models.signals import post_save
import json
import traceback
import os
import sys

CLIENT_ID="6fc75b2329dc4ef8a813ea4852da9a76"
CLIENT_SECRET="a431a75619e84ff59ce21b09a12d93a9"
CALLBACK_HOST="http://insta.gangverk.is"

api = InstagramAPI(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
reactor = subscriptions.SubscriptionsReactor()

# endpoint that receives the pushed requests from instagram
def instagramPushListener( request, subscriber_id ):
	'''
	Handles the realtime API callbacks

	If request is a GET then we assume that the request is an echo request
	Else we assume that we are receiving data from the source
	'''
	if request.method == "POST":
		print >> sys.stderr, "Starting processing"
		x_hub_signature = request.META.get('HTTP_X_HUB_SIGNATURE')
		raw_response = request.body
		tb = None

		try:
			reactor.process(CLIENT_SECRET, raw_response, x_hub_signature)
		except Exception as e:
			print >> sys.stderr, "Got error in reactor processing"
			exc_type, exc_value, exc_traceback = sys.exc_info()
			print >> sys.stderr, repr(traceback.format_exception(exc_type, exc_value,exc_traceback))
	else:
		return echoInstagramVerifyToken( request )

	return HttpResponse("")

# Business end of this view, faces the client
def instagramTagStream( request, tag ):
	'''
	Streams the given tag
	'''
	#Params:
	#Paging index
	#No of results per response, max 30
	
	images = instagramStream( request, "tag", tag )

	result = []
	for img in images:
		result.append( img.toDict() )

	return HttpResponse( json.dumps(result), mimetype="application/json")

def instagramStream( request, object_type, object_value=None, lat=None, lng=None, radius=None ):
	data = None	

	if object_type == "geography":
		data = Subscription.objects.filter( object_type=object_type, lat=lat, lng=lng, radius=radius )
	else:
		data = Subscription.objects.filter( object_type=object_type, object_value=object_value )

	data.get();
	images = InstagramImage.objects.filter(subscriber=data)

	return images

def testApi( request ):
	media,next = api.tag_recent_media( 30, 0, "gangverk")

	subscribe_data = {"id":1}
	processImages( media, subscribe_data )

	return HttpResponse( "OK" )

def processUserUpdate( update ):
	media, next = api.user_recent_media( 30, 0, update['object_id'])
	processImages( media, update )

def processTagUpdate( update ):
	media, next = api.tag_recent_media( 30, 0, update['object_id'] )
	processImages( media, update )

def processLocationUpdate( update ):
	media, next = api.location_recent_media( 30, 0, update['object_id'] )
	processImages( media, update )

def processGeographyUpdate( update ):
	media, next = api.geography_recent_media( 30, 0, update['object_id'] )
	processImages( media, update )

def processImages( media, data ):
	for image in media:
		db_image = InstagramImage()
		db_image.thumbnail_url = image.images['thumbnail'].url
		db_image.full_url = image.images['standard_resolution'].url
		db_image.caption = getattr(image.caption, "text", "")
		db_image.user = image.user.id
		db_image.subscriber = Subscription.objects.get( remote_id=data['subscription_id'] )
		db_image.all_tags = json.dumps([i.name for i in image.tags])
		db_image.comments = json.dumps([{"user":i.user.id, "text":i.text} for i in image.comments])
		if hasattr(image, "location"):
			db_image.location = image.location.name
			db_image.lat = image.location.point.latitude
			db_image.lng = image.location.point.longitude
		db_image.save()

def echoInstagramVerifyToken( request ):
	'''
	Echo service to verify that we made the request
	'''
	echo = ""
	if request.GET.has_key('hub.challenge'):
		echo = request.GET['hub.challenge']
	return HttpResponse(echo)

def registerListener(**kwargs):
	'''
	Trigger that is invoked when a hashtag is registered or updated using the model save method
	'''
	instance = kwargs['instance']
	object_type = instance.object_type
	object_value = instance.object_value
	callback_url = "{0}/instagramPush/{1}".format(CALLBACK_HOST, instance.id)
	res = None
	if object_type == "geography":
		res = api.create_subscription( object=object_type, aspect='media', lat=instance.lat, lng=instance.lng, radius=instance.radius, callback_url=callback_url )
	else:
		res = api.create_subscription( object=object_type, object_id=object_value, aspect='media', callback_url=callback_url )

	instance.remote_id = res['data']['id']
	instance.save()

#Register the listener for the databaseupdates for table Subscription
post_save.connect(registerListener, sender=Subscription)

reactor.register_callback(subscriptions.SubscriptionType.USER, processUserUpdate)
reactor.register_callback(subscriptions.SubscriptionType.TAG, processTagUpdate)
reactor.register_callback(subscriptions.SubscriptionType.LOCATION, processLocationUpdate)
reactor.register_callback(subscriptions.SubscriptionType.GEOGRAPHY, processGeographyUpdate)

