from django.http import HttpResponse
from instagram.client import InstagramAPI
from instagram.models import Subscription
from instagram.models import InstagramImage
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
		recent = result api.tag_recent_media(30, 0, tag_name)
		
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
	#Paging index
	#No of results per response, max 30
	return HttpResponse("Hello, world. you are pulling data from me {0}".format(tag))


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
	tag = instance.tag_name
	api.create_subscription( object='tag', object_id=tag, aspect='media', callback_url="http://insta.gangverk.is/{0}/instagramPush".format(tag) )

	print "Register new callback subscription for {0}".format(instance.tag_name)
	print kwargs

#Register the listener for the databaseupdates for table Subscription
post_save.connect(registerListener, sender=Subscription)