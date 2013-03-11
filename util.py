#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#

import hashlib
import json
import re


NOT_USER_PATTERN = re.compile("[^a-z0-9]")
EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-])*\.[a-zA-Z]{2,4}$")


def yagra_check_email_valid(email):
    "检查email字符结构是否合法"
    return bool(EMAIL_PATTERN.match(email))


def yagra_check_username_valid(username):
    "检查用户名字符是否合法"
    return not bool(NOT_USER_PATTERN.search(username))


def json_encode(value):
    return json.dumps(value).replace("</", "<\\/")


def utf8(value):
    if isinstance(value, (type(None), str)):
        return value
    assert isinstance(value, unicode)
    return value.encode("utf-8")


def import_object(name):
    parts = name.split('.')
    obj = __import__('.'.join(parts[:-1]), None, None, [parts[-1]], 0)
    return getattr(obj, parts[-1])


def flatten(nested):
    flat = list()
    def flatten_in(nested, flat):
        for i in nested:
            flatten_in(i, flat) if isinstance(i, (list, tuple)) else flat.append(i)
        return flat
    flatten_in(nested, flat)
    return flat


PASSWORD_SALT = "http://EverET.org"


def hash_password(pwd):
    "用sha1加上salt进行加密"
    h = hashlib.sha1()
    h.update(PASSWORD_SALT)
    h.update(pwd)
    return h.hexdigest()
