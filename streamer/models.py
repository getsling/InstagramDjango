from django.db import models

class Subscription(models.Model):
	'''
	Supports all subscriptions for Instagram
	Keeping them here is for error recovery.

	When adding to this table the subscription request
	gets automatically sent using the post_save event.
	The listener for the event is registered in the views.py
	'''

	SUBSCRIPTION_TYPES = (
	    ('tag', 'Tag'),
	    ('user', 'User'),
	    ('location', 'Location'),
	    ('geography', 'Geography')
	)

	#Subscription type
	object_type = models.CharField( max_length=12, choices=SUBSCRIPTION_TYPES )
	#The value requested in the subscription
	object_value = models.CharField( max_length=512 )
	
	#The next 3 fields are only used for geography subscriptions
	lat = models.DecimalField( max_digits=10, decimal_places=7, default=0, blank=True )
	lng = models.DecimalField( max_digits=10, decimal_places=7, default=0, blank=True )
	#Radius in meters
	radius = models.IntegerField( default=0, blank=True )

class InstagramImage(models.Model):
	'''
	This is our object cache in order to minimize the api traffic.

	Subscriber that requested the item is ForeignKey
	'''
	#The requester
	subscriber = models.ForeignKey( Subscription )

	#Location information
	location = models.CharField( max_length=512 )

	#Geography information
	lat = models.DecimalField( max_digits=10, decimal_places=7, default=0, blank=True )
	lng = models.DecimalField( max_digits=10, decimal_places=7, default=0, blank=True )

	#Json string containing a list of all tags
	all_tags = models.CharField( max_length=512 )
	#The raw caption
	caption = models.CharField( max_length=512 )
	#Id of the instagram user
	user = models.IntegerField()
	#The url to the thumbnail
	thumbnail_url = models.CharField( max_length=512 )
	#Url to the full image
	full_url = models.CharField( max_length=512 )
	