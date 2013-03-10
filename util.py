#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#

import hashlib
import logging


def utf8(value):
    if isinstance(value, (type(None), str)):
        return value
    if not isinstance(value, unicode):
        logging.info("utf8(): value is not unicode " + str(type(value)))

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
            flatten_in(i, flat) if isinstance(i, list) else flat.append(i)
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
