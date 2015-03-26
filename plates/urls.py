from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from plates import views

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='index'),
    #since we want that this is not accessible to unlogged people we put the decorator around the call to view.**.as_view
    url(r'^(?P<pk>\d+)/$', login_required(views.PlateView.as_view()), name='plate'),
    #Here the variable well will be available in self.kwargs["well"] in views.WellView instances
    url(r'^(?P<pk>\d+)/w(?P<well>\d+)/$', login_required(views.WellView.as_view()), name='well')
)