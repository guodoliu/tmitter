from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^p/(?P<page_index>\d+)/$', views.index_page),
    url(r'^user/$', views.index_user_self),
    url(r'^user/(?P<username>[a-zA-Z\-_\d]+)/$', views.index_user, name='tmitter-mvc-views-index_user'),
    url(r'^user/(?P<username>[a-zA-Z\-_\d]+)/(?P<page_index>\d+)/$', views.index_user_page),
    url(r'^users/$', views.users_index),
    url(r'^users/(?P<page_index>\d+)/$', views.users_list),
    url(r'^signup/$', views.signup),
    url(r'^signin/$', views.signin),
    url(r'^signout/$', views.signout),
    url(r'^settings/$', views.settings, name='tmitter-mvc-views-settings'),
    url(r'^message/(?P<id>\d+)/$', views.detail, name='tmitter-mvc-views-detail'),
    url(r'^message/(?P<id>)\d+/delete/$', views.detail_delete, name='tmitter-mvc-views-detail_delete'),
    url(r'^friend/add/(?P<username>[a-zA-Z\-_\d]+)', views.friend_add, name='tmitter-mvc-views-friend_add'),
    url(r'^friend/remove/(?P<username>[a-zA-Z\-_\d]+)', views.friend_remove, name='tmitter-mvc-views-friend_remove'),
    url(r'^api/note/add/', views.api_note_add),
]