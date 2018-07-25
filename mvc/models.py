# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from utils import function, formatter

# Create your models here.


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