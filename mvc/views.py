# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import Context, loader
from django.utils.translation import ugettext as _
from .models import User, Area
from utils import mailer, formatter, function, uploader

# Create your views here.


def __do_login(request, _username, _password):
    _state = __check_login(_username, _password)
    if _state['success']:
        request.session['islogin'] = True
        request.session['userid'] = _state['userid']
        request.session['username'] = _username
        request.session['realname'] = _password

    return _state


def __user_id(request):
    return request.session.get('userid', -1)


def __user_name(request):
    return request.session.get('username', '')


def __is_login(request):
    return request.session.get('islogin', False)


def __check_login(_username, _password):
    _state = {
        'success': True,
        'message': 'none',
        'userid': -1,
        'realname': '',
    }

    try:
        _user = User.objects.get(username=_username)
        if _user.password == function.md5_encode(_password):
            _state['success'] = True
            _state['userid'] = _user.id
            _state['realname'] = _user.realname
        else:
            _state['success'] = False
            _state['message'] = _('Password incorrect.')
    except (User.DoesNotExist):
        _state['success'] = False
        _state['message'] = _('User does not exist.')

    return _state


def __check_username_exist(_username):
    _exist = True

    try:
        _user = User.objects.get(username=_username)
        _exist = True
    except User.DoesNotExist:
        _exist = False

    return _exist


def __do_signup(request, _userinfo):

    _state = {
        'success': False,
        'message': '',
    }

    if _userinfo['username'] == '':
        _state['success'] = False
        _state['message'] = _('"Username" have not inputed.')
        return _state

    if _userinfo['password'] == '':
        _state['success'] = False
        _state['message'] = _('"Password" have not inputed.')
        return _state

    if _userinfo['realname'] == '':
        _state['success'] = False
        _state['message'] = _('"Real Name" have not inputed.')
        return _state

    if _userinfo['email'] == '':
        _state['success'] = False
        _state['message'] = _('"Email" have not inputed.')
        return _state

    if __check_username_exist(_userinfo['username']):
        _state['success'] = False
        _state['message'] = _('"Username" have not existed.')
        return _state

    if _userinfo['password'] != _userinfo['confirm']:
        _state['success'] = False
        _state['message'] = _('"Confirm Password" have not match.')
        return _state

    _user = User(
        username=_userinfo['username'],
        realname=_userinfo['realname'],
        password=_userinfo['password'],
        email=_userinfo['email'],
        area=Area.objects.get(id=1)
    )

    _user.save()
    _state['success'] = True
    _state['message'] = _('Successed.')

    mailer.send_regist_success_mail(_userinfo)
    return _state


# response result message page
def __result_message(request, _title=_('Message'), _message=_('Unknown error, processing interrupted.'), _go_back_url=''):
    _islogin = __is_login(request)

    if _go_back_url == '':
        _go_back_url = function.get_referer_url(request)

    # body content
    _template = loader.get_template('result_message.html')

    _context = Context({
        'page_title': _title,
        'message': _message,
        'go_back_url': _go_back_url,
        'islogin': _islogin
    })

    _output = _template.render(_context)
    return HttpResponse(_output)


def signin(request):
    # get user login status
    _islogin = __is_login(request)

    try:
        # get post params
        _username = request.POST['username']
        _password = request.POST['password']
        _is_post = True
    except KeyError:
        _is_post = False

    # check username and password
    if _is_post:
        _state = __do_login(request, _username, _password)

        if _state['success']:
            return __result_message(request, _('Login successed'), _('You are logined now.'))
    else:
        _state = {
            'success': False,
            'message': _('Please login first.')
        }

    # body content
    _template = loader.get_template('signin.html')
    _context = {
        'page_title': _('Signin'),
        'state': _state,
    }
    _output = _template.render(_context)
    return HttpResponse(_output)


def signup(request):
    # check is login
    _islogin = __is_login(request)

    if _islogin:
        return HttpResponseRedirect('/')

    _userinfo = {
        'username': '',
        'password': '',
        'confirm': '',
        'realname': '',
        'email': '',
    }

    try:
        _userinfo = {
            'username': request.POST['username'],
            'password': request.POST['password'],
            'confirm': request.POST['confirm'],
            'realname': request.POST['realname'],
            'email': request.POST['email'],
        }
        _is_post = True
    except KeyError:
        _is_post = False

    if _is_post:
        _state = __do_signup(request, _userinfo)
    else:
        _state = {
            'success': False,
            'message': _('Signup')
        }

    if _state['success']:
        return __result_message(request, _('Signup successed'), _('Your account was registered success.'))

    _result = {
        'success': _state['success'],
        'message': _state['message'],
        'form': {
            'username': _userinfo['username'],
            'realname': _userinfo['realname'],
            'email': _userinfo['email'],
        }
    }

    # body content
    _template = loader.get_template('signup.html')
    _context = {
        'page_title': _('Signup'),
        'state': _result,
    }
    _output = _template.render(_context)
    return HttpResponse(_output)
