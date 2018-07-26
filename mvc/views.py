# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import Context, loader
from django.utils.translation import ugettext as _
from .models import User, Area, Category, Note
from tmitter.settings import *
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


# ###############
# view method
# ###############

# home view
def index(request):
    return index_user(request, '')


# user messages view by self
def index_user_delf(request):
    _user_name = __user_name(request)
    return index_user(request, _user_name)


# user messages view
def index_user(request, _username):
    return index_user_page(request, _username, 1)


# index page
def index_page(request, _page_index):
    return index_user_page(request, '', _page_index)


# user message view and page
def index_user_page(request, _username, _page_index):
    # get user login status
    _islogin = __is_login(request)
    _page_title = _('Home')

    try:
        # get post params
        _message = request.POST['message']
        _is_post = True
    except KeyError:
        _is_post = False

    # save message
    if _is_post:
        # check login
        if not _islogin:
            return HttpResponseRedirect('/signin/')

        # save messages
        (_category, _is_added_cate) = Category.objects.get_or_create(name=u'网页')

        try:
            _user = User.objects.get(id=__user_id(request))
        except:
            return HttpResponseRedirect('/signin/')

        _note = Note(message=_message, category=_category, user=_user)
        _note.save()

        return HttpResponseRedirect('/user/' + _user.username)

    # get message list
    _offset_index = (int(_page_index) - 1) * PAGE_SIZE
    _last_item_index = PAGE_SIZE * int(_page_index)

    _login_user_friend_list = None
    if _islogin:
        # get friend messages if user is logined
        _login_user = User.objects.get(username=__user_name(request))
        _login_user_friend_list = _login_user.friend.all()
    else:
        _login_user = None

    _friends = None
    _self_home = False
    if _username != '':
        # there is get user's messages
        _user = get_object_or_404(User, username=_username)
        _userid = _user.id
        _notes = Note.objects.filter(user=_user).order_by('-addtime')
        _page_title = u'%s' % _user.realname
        #get friend list
        _friends = _user.friend.order_by("id")[0:FRIEND_LIST_MAX]
        print "..................", _friends
        if _userid == __user_id(request):
            _self_home = True
    else:
        _user = None

        if _islogin:
            _query_users = [_login_user]
            _query_users.extend(_login_user.friend.all())
            _notes = Note.objects.filter(user__in=_query_users).order_by('-addtime')
        else:
            _notes = []

    # page bar
    _page_bar = formatter.pagebar(_notes, _page_index, _username)

    # get current page
    _notes = _notes[_offset_index : _last_item_index]

    # body content
    _template = loader.get_template('index.html')

    _context = {
        'page_title': _page_title,
        'notes': _notes,
        'islogin': _islogin,
        'userid': __user_id(request),
        'self_home': _self_home,
        'user': _user,
        'page_bar': _page_bar,
        'friends': _friends,
        'login_user_friend_list': _login_user_friend_list,
    }

    _output = _template.render(_context)
    return HttpResponse(_output)


def detail(request, _id):
    _islogin = __is_login(request)

    _note = get_object_or_404(Note, id=_id)

    # body content
    _template = loader.get_template('detail.html')
    _context = {
        'page_title': _('%s\'s message %s') % (_note.user.realname, _id),
        'item': _note,
        'islogin': _islogin,
        'userid': __user_id(request),
    }

    _output = _template.render(_context)
    return HttpResponse(_output)


def detail_delete(request, _id):
    # get user login status
    _islogin = __is_login(request)

    _note = get_object_or_404(Note, id=_id)
    _message = ""

    try:
        _note.delete()
        _message = _('Message deleted.')
    except:
        _message = _('Delete failed.')

    return __result_message(request, _('Message %s') % _id, _message)


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


def signout(request):
    request.session['islogin'] = False
    request.session['userid'] = -1
    request.session['username'] = ''

    return HttpResponseRedirect('/')