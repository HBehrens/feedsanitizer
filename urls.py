from django.conf.urls.defaults import *

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    ('^_ah/warmup$', 'djangoappengine.views.warmup'),
    
    ('^$', 'views.userfriendly'),
    
    (r'^sanitize$', 'views.sanitize'),
)
