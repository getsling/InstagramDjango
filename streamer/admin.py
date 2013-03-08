from django.contrib import admin
from streamer.models import Subscription
from streamer.models import InstagramImage
from streamer.models import SubscriptionAdmin
from streamer.models import InstagramImageAdmin
from streamer.models import InstagramEndpoint

admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(InstagramImage, InstagramImageAdmin)
admin.site.register(InstagramEndpoint)