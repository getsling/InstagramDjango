import urllib
import urllib2
import socket

class InstagramHelper:
	'''
	Instagram API helper

	Manages subscriptions to Instagram realtime API
	author: arnaldur@gangverk.is
	'''
	
	client_id = "";
	client_secret = "";

	available_subscription_types = ['user','tag','location','geography']
	instagram_host = "api.instagram.com"

	def __init__( self, client_id=None, client_secret=None ):
		self.client_id = client_id
		self.client_secret = client_secret

		if not socket.ssl:
			print "No SSL installed!! Cannot use HTTPS"


	#A function that registeres the push endpoint with the realtime api
	def registerPushEndpoint( self, key, value, callback_url ):
		'''
			curl -F 'client_id=CLIENT-ID' \
			-F 'client_secret=CLIENT-SECRET' \
			-F 'object=tag' \
			-F 'aspect=media' \
			-F 'object_id=nofilter' \
			-F 'callback_url=http://YOUR-CALLBACK/URL' \
			https://api.instagram.com/v1/subscriptions/
		'''
		params = {}
		params['client_id'] = self.client_id
		params['client_secret'] = self.client_secret
		params['object'] = key
		params['object_id'] = value
		params['callback_url'] = callback_url

		instagram_url = "https://{0}/v1/subscriptions/".format( self.instagram_host )
		headers = urllib.urlencode(params) # parameters is dicitonar
		req = urllib2.Request(instagram_url, headers) # PP_URL is the destionation URL
		req.add_header("Content-type", "application/x-www-form-urlencoded")
		response = urllib2.urlopen(req)

		'''
		//Example response from instagram
		{
		    "meta": {
		        "code": 200
		    },
		    "data": [
		        {
		            "id": "1",
		            "type": "subscribe",
		            "object": "user",
		            "aspect": "media",
		            "callback_url": "http://your-callback.com/url/"
		        },
		        {
		            "id": "2",
		            "type": "subscription",
		            "object": "location",
		            "object_id": "2345",
		            "aspect": "media",
		            "callback_url": "http://your-callback.com/url/"
		        }
		    ]
		}		
		'''
		
		print response

	def getSubscriptions():
		url_string = '/v1/subscriptions?client_secret={0}&client_id={1}'.format( self.client_secret, self.client_id )
		self.callUrlWithMethod( url_string, 'GET' )

	def cancelAllSubscriptions():
		url_string = '/v1/subscriptions?client_secret={0}&client_id={1}&object=all'.format( self.client_secret, self.client_id )
		self.callUrlWithMethod( url_string, 'DELETE' )

	def cancelSubscription( subscription_id ):
		url_string = '/v1/subscriptions?client_secret={0}&client_id={1}&id={2}'.format( self.client_secret, self.client_id, subscription_id)
		self.callUrlWithMethod( url_string, 'DELETE' )

	def cancelAllSubscriptionsOfType( type_string ):
		if type_string in self.available_subscription_types:
			url_string = '/v1/subscriptions?client_secret={0}&client_id={1}&object={2}'.format( self.client_secret, self.client_id, type_string)
			self.callUrlWithMethod( url_string, 'DELETE' )
		else
			pass
			#TODO: add error handling

	def callUrlWithMethod( url, method ):
		import httplib 
		conn = httplib.HTTPSConnection(self.instagram_host)
		conn.request(method, url, body)
		resp = conn.getresponse()
		content = resp.read()

if __name__ == "__main__":
	print "Init the helper class"
	helper = InstagramHelper('test1','test2')
	print helper.client_id
	print helper.client_secret

	print helper.registerPushEndpoint('tag','airwaves12','http://hashstream.gangverk.is/airwaves12/instagramPush')

	#A function that knows how to get the latest stuff for a given tag