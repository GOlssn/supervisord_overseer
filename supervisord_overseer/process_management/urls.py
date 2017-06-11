from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from django.views.generic.base import RedirectView

import process_management.views as views

urlpatterns = [
    url(r'^ajax/restart_process', login_required(views.AjaxRestartProcessView.as_view()), name='restart_process'),
    url(r'^ajax/stop_process', login_required(views.AjaxStopProcessView.as_view()), name='stop_process'),
    url(r'^node/(?P<node>.+)/$', login_required(views.SingleNodeView.as_view()), name='single_node'),
    url(r'^group/(?P<group>.+)/$', login_required(views.SingleGroupView.as_view()), name='single_group'),
    url(r'^nodes/$', login_required(views.AllNodesView.as_view()), name='all_nodes'),
    url(r'^dashboard$', login_required(views.IndexView.as_view()), name='index'),
    url(r'^$', RedirectView.as_view(pattern_name='index'))
]

