from django.http import HttpResponse
from instagram.client import InstagramAPI
from instagram import subscriptions
from models import Subscription
from models import InstagramImage
from django.db.models.signals import post_save

CLIENT_ID="6fc75b2329dc4ef8a813ea4852da9a76"
CLIENT_SECRET="a431a75619e84ff59ce21b09a12d93a9"

api = InstagramAPI(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

# endpoint that receives the pushed requests from instagram
def instagramPushListener( request, tag ):
	'''
	Handles the realtime API callbacks

	If request is a GET then we assume that the request is an echo request
	Else we assume that we are receiving data from the source
	'''
	if request.method == "POST":
		recent = api.tag_recent_media(30, 0, tag)
		
		for media in recent:
			media.images.thumbnail.url
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

	return HttpResponse(json.dumps(images), mimetype="application/json")

def instagramStream( request, object_type, object_value=None, lat=None, lng=None, radius=None ):
	data = None

	if object_type == "geography":
		data = Subscription.objects.filter( object_type=object_type, lat=lat, lng=lng, radius=radius)
	else:
		data = Subscription.objects.filter( object_type=object_type, object_value=object_value )

	data.get();
	images = InstagramImage.objects.filter(subscriber=data)

	return images

def processUserUpdate( update ):
	pass

def processTagUpdate( update ):
	processImages( api.tag_recent_media( 30, 0, update.object_id ) )

def processLocationUpdate( update ):
	pass

def processGeographyUpdate( update ):
	pass

def processImages( data ):


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
	callback_url = "http://insta.gangverk.is/instagramPush/{0}".format(instance.id)
	
	if object_type == "geography":
		api.create_subscription( object=object_type, aspect='media', lat=instance.lat, lng=instance.lng, radius=instance.radius, callback_url=callback_url )
	else:
		api.create_subscription( object=object_type, object_id=object_value, aspect='media', callback_url=callback_url )

	print "Register subscription for {0} with value: {1}".format(object_type, object_value)
	print kwargs

#Register the listener for the databaseupdates for table Subscription
post_save.connect(registerListener, sender=Subscription)

reactor = subscriptions.SubscriptionsReactor()
reactor.register_callback(subscriptions.SubscriptionType.USER, processUserUpdate)
reactor.register_callback(subscriptions.SubscriptionType.TAG, processTagUpdate)
reactor.register_callback(subscriptions.SubscriptionType.LOCATION, processLocationUpdate)
reactor.register_callback(subscriptions.SubscriptionType.GEOGRAPHY, processGeographyUpdate)

