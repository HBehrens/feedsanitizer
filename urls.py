from django.conf.urls.defaults import *

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    ('^_ah/warmup$', 'djangoappengine.views.warmup'),
    
    ('^$', 'views.userfriendly'),
    
    (r'^sanitize$', 'views.sanitize'),
    
    (r'^tests$', 'django.views.generic.simple.direct_to_template', {'template':'tests.html'}),
    
    (r'^validate$', 'testviews.validate'),
)
