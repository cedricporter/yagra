#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#


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
