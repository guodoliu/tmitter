# -*- coding: utf-8 -*-
from django.template import Library


register = Library()


def in_list(val, lst):
    return val in lst


register.filter("in_list", in_list)