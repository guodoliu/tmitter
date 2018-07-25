# -*- coding: utf-8 -*-
import md5


def md5_encode(str):
    """
    summary: MD5 encode
    """
    return md5.new(str).hexdigest()


def get_referer_url(request):
    """
    summary: get request referer url address, default /
    """
    return request.META.get('HTTP_REFERER', '/')
