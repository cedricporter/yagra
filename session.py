#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#

import pickle
import base64


class Session(object):
    def __init__(self):
        self._data = {}

    def __contains__(self, name):
        return name in self._data

    def __getattr__(self, name):
        return self._data[name]

    def __setattr__(self, name, value):
        self._data[name] = value

    def __delattr__(self, name):
        del self._data[name]


class Store(object):
    def __contains__(self, key):
        raise NotImplementedError

    def __getitem__(self, key):
        raise NotImplementedError

    def __setitem__(self, key, value):
        raise NotImplementedError

    def encode(self, session_dict):
        pickled = pickle.dumps(session_dict)
        return base64.encodestring(pickled)

    def decode(self, session_data):
        pickled = base64.decodestring(session_data)
        return pickle.loads(pickled)


class MySQLStore(Store):
    def __init__(self, db, table_name):
        self.db = db
        self.table = table_name
