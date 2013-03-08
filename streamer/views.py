from django.http import HttpResponse
from instagram.client import InstagramAPI
from instagram import subscriptions
from models import Subscription
from models import InstagramImage
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
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
def instagramPushListener( request, subscriber_django_id ):
	'''
	Handles the realtime API callbacks

	If request is a GET then we assume that the request is an echo request
	Else we assume that we are receiving data from the source
	'''
	if request.method == "POST":
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
	images = InstagramImage.objects.filter(subscriber=data).order_by('-created_time')

	return images

def testApi( request ):
	media,next = api.tag_recent_media( 30, 0, "gangverk")

	#The id is supplied from instagram
	subscribe_data = {"subscription_id":2807743}
	processImages( media, subscribe_data )

	return HttpResponse( "OK" )

def processInstagramUpdate( update ):
	key = update['object']
	subscription_id = update['subscription_id']
	
	val = update.get('object_id')
 
	if key == 'geography':
		requestMediaByGeography( lat, lng, radius, subscription_id )
	elif key == 'tag':
		requestMediaByTag( val, subscription_id )
	elif key == 'user':
		requestMediaByUser( val, subscription_id )
	elif key == 'location':
		requestMediaByLocation( val, subscription_id )

def requestMediaByUser( user_id, subscription_id ):
	media, next = api.user_recent_media( 30, 0, user_id)
	processImages( media, subscription_id )

def requestMediaByTag( tag, subscription_id ):
	media, next = api.tag_recent_media( 30, 0, tag)
	processImages( media, subscription_id )

def requestMediaByLocation( location, subscription_id ):
	media, next = api.location_recent_media( 30, 0, location )
	processImages( media, subscription_id )

def requestMediaByGeography( lat, lng, radius, subscription_id ):
	media, next = api.geography_recent_media( 30, 0 )
	processImages( media, subscription_id )

def processImages( media, subscription_id ):
	for image in media:
		image_query = InstagramImage.objects.filter(remote_id=image.id)
		if len(image_query) == 1:
			db_image = image_query[0]
		else:
			db_image = InstagramImage()
			db_image.remote_id = image.id
			db_image.thumbnail_url = image.images['thumbnail'].url
			db_image.full_url = image.images['standard_resolution'].url
			db_image.user = image.user.id
			db_image.username = image.user.username
			db_image.usericon = image.user.profile_picture
			db_image.subscriber = Subscription.objects.get( remote_id= subscription_id )
			db_image.likescount = len(image.likes)
			db_image.created_time = image.created_time
		db_image.caption = getattr(image.caption, "text", "")
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

def registerInstagramListener(**kwargs):
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
	elif object_type == "user":
		print "Handling user"
		user_res = api.user_search(q=object_value, count=1)
		user_id = [ i.id for i in user_res if i.username == object_value][0]

		object_value = user_id

		res = api.create_subscription( object=object_type, object_id=user_id, aspect='media', callback_url=callback_url )
	else:
		res = api.create_subscription( object=object_type, object_id=object_value, aspect='media', callback_url=callback_url )


	#Disconnect the handler so we don't fall into endless loop
	post_save.disconnect(registerInstagramListener, sender=Subscription)
	instance.remote_id = res['data']['id']
	instance.save()
	post_save.connect(registerInstagramListener, sender=Subscription)

	#Populate the subscription with recent media
	update = {'object':object_type,'object_id':object_value, 'subscription_id': instance.remote_id }
	processInstagramUpdate(update)

def removeInstagramListener(**kwargs):
	'''
	Trigger to cancel subscription with instagram when a subscription object is deleted
	'''
	instance = kwargs['instance']
	api.delete_subscriptions(id=instance.id)

#Register the listener for the databaseupdates for table Subscription
post_save.connect(registerInstagramListener, sender=Subscription)
post_delete.connect(removeInstagramListener, sender=Subscription)

#Register the handlers for updates in the Instagram API
reactor.register_callback(subscriptions.SubscriptionType.USER, processInstagramUpdate)
reactor.register_callback(subscriptions.SubscriptionType.TAG, processInstagramUpdate)
reactor.register_callback(subscriptions.SubscriptionType.LOCATION, processInstagramUpdate)
reactor.register_callback(subscriptions.SubscriptionType.GEOGRAPHY, processInstagramUpdate)

