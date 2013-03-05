from django.db import models
import json
from django.core import serializers
from django.contrib import admin

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

	remote_id = models.IntegerField( default=0, blank=True )

	#Subscription type
	object_type = models.CharField( max_length=12, choices=SUBSCRIPTION_TYPES )
	#The value requested in the subscription
	object_value = models.CharField( max_length=512 )

	#The next 3 fields are only used for geography subscriptions
	lat = models.DecimalField( max_digits=10, decimal_places=7, default=0, blank=True )
	lng = models.DecimalField( max_digits=10, decimal_places=7, default=0, blank=True )
	#Radius in meters
	radius = models.IntegerField( default=0, blank=True )

	def __unicode__(self):
		return "{0} is \"{1}\"".format( self.object_type, self.object_value )

class SubscriptionAdmin(admin.ModelAdmin):
	exclude = ['remote_id']

class InstagramImage(models.Model):
	'''
	This is our object cache in order to minimize the api traffic.

	Subscriber that requested the item is ForeignKey
	'''

	def toDict(self):
		obj = {
			'lat':str(self.lat),
			'lng':str(self.lng),
			'all_tags':self.all_tags,
			'caption':self.caption,
			'thumbnail_url':self.thumbnail_url,
			'full_url':self.full_url,
			'comments': json.loads(self.comments),
			'location':self.location,
			'user':self.user,
			'username':self.username,
			'usericon':self.usericon,
			'likescount':self.likescount
		}
		return obj

	remote_id = models.CharField( max_length=256, unique=True)

	#The requester
	subscriber = models.ForeignKey( Subscription )

	#Location information
	location = models.CharField( max_length=512 )

	#Geography information
	lat = models.DecimalField( max_digits=10, decimal_places=7, default=0, blank=True )
	lng = models.DecimalField( max_digits=10, decimal_places=7, default=0, blank=True )

	#Json string containing a list of all tags
	all_tags = models.CharField( max_length=512, default="", blank=True  )
	#The raw caption
	caption = models.CharField( max_length=512, default="", blank=True )
	#Comments on the image
	comments = models.TextField( )
	#Id of the instagram user
	user = models.IntegerField()
	username = models.CharField( max_length=512, default="", blank=True )
	usericon = models.CharField( max_length=512, default="", blank=True )

	likescount = models.IntegerField()

	#The url to the thumbnail
	thumbnail_url = models.CharField( max_length=512 )
	#Url to the full image
	full_url = models.CharField( max_length=512 )

	def __unicode__(self):
		return self.caption

	def admin_image(self):
		return '<img src="%s"/>' % self.thumbnail_url

	admin_image.allow_tags = True
	admin_image.short_description = 'Image thumbnail'

class InstagramImageAdmin(admin.ModelAdmin):
	read_only = ('instagram_id')  
	list_display = ('subscriber','caption','admin_image')
	
