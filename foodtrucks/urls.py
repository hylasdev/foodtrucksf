from django.conf.urls import patterns, url

from foodtrucks import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^get_trucks/', views.get_trucks, name='get_truck'),
)
