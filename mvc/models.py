# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib import admin
from django.utils import timesince,html
from utils import function, formatter
from tmitter.settings import *
from django.utils.encoding import python_2_unicode_compatible

# Create your models here.


@python_2_unicode_compatible
class Category(models.Model):
    name = models.CharField('名称', max_length=20)

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        self.name = self.name[0:20]
        return super(Category, self).save()

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'
    
    def __str__(self):
        return self.name


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    list_per_page = ADMIN_PAGE_SIZE


class Area(models.Model):
    TYPE_CHOICES = {
        (0, 'Country'),
        (1, 'Province'),
        (2, 'City'),
        (3, 'District'),
    }

    name = models.CharField('Location', max_length=100)
    code = models.CharField('Code', max_length=255)
    type = models.IntegerField('Type', choices=TYPE_CHOICES)
    parent = models.IntegerField('Parent Number(Associated with yourself)')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'Location'
        verbose_name_plural = u'Location'


class AreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code')
    list_display_links = ('id', 'name', 'code')
    list_per_page = ADMIN_PAGE_SIZE


class User(models.Model):
    id = models.AutoField(primary_key=True)

    username = models.CharField('Username', max_length=20)
    password = models.CharField('Password', max_length=100)
    realname = models.CharField('Realname', max_length=20)
    email = models.EmailField('Email')
    area = models.ForeignKey(Area, verbose_name='Diqu')
    face = models.ImageField('Face', upload_to='face/%Y/%m/%d', default='', blank=True)
    url = models.CharField('Personal Page', max_length=200, default='', blank=True)
    about = models.TextField('About Me', max_length=1000, default='', blank=True)
    addtime = models.DateTimeField('Signup Time', auto_now=True)
    friend = models.ManyToManyField("self", verbose_name='Friends')

    def __unicode__(self):
        return self.username

    def addtime_format(self):
        return self.addtime.strftime('%Y-%m-%d %H:%M:%S')

    def save(self, modify_pwd=True):
        if modify_pwd:
            self.password = function.md5_encode(self.password)
        self.about = formatter.substr(self.about, 20, True)
        super(User, self).save()

    class Meta:
        verbose_name = u'User Name'
        verbose_name_plural = u'User Name'


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'realname', 'email', 'addtime_format')
    list_display_links = ('username', 'realname', 'email')
    list_per_page = ADMIN_PAGE_SIZE


class Note(models.Model):
    id = models.AutoField(primary_key=True)
    message = models.TextField('News')
    addtime = models.DateTimeField('Publish Time', auto_now=True)
    category = models.ForeignKey(Category, verbose_name='Source')
    user = models.ForeignKey(User, verbose_name='Publisher')

    def __unicode__(self):
        return self.message

    def message_short(self):
        return formatter.substr(self.message, 30)

    def addtime_format_admin(self):
        return self.addtime.strftime('%Y-%m-%d %H:%M:%S')

    def category_name(self):
        return self.category.name

    def user_name(self):
        return self.user.realname

    def save(self):
        self.message = formatter.content_tiny_url(self.message)
        self.message = html.escape(self.message)
        self.message = formatter.substr(self.message, 140)
        super(Note, self).save()

    class Meta:
        verbose_name = u'消息'
        verbose_name_plural = u'消息'

    def get_absolute_url(self):
        return APP_DOMAIN + 'message/%s/' %self.id


class NoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_name', 'message_short', 'addtime_format_admin', 'category_name')
    list_display_links = ('id', 'message_short')
    search_fields = ['message']
    list_per_page = ADMIN_PAGE_SIZE