from django.conf.urls import patterns, url

from uploader.packages import views

urlpatterns = patterns('',
                       url(r'^(?P<package_id>\d+)/$', views.show, name='show'),
                       url(r'^(?P<package_id>\d+)/remove/$', views.remove, name='remove'),
                       url(r'^(?P<package_id>\d+)/clear/$', views.clear, name='clear'),
)