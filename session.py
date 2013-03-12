#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#

import pickle
import base64
import time
import datetime
import uuid


class Session(object):
    def __init__(self, store, handler):
        self._data = {}
        self.store = store
        self.handler = handler

    def __contains__(self, name):
        return name in self._data

    def __getitem__(self, name):
        return self._data[name]

    def __setitem__(self, name, value):
        self._data[name] = value

    def __delitem__(self, name):
        del self._data[name]

    def get(self, name, default=None):
        return self._data.get(name, default)

    def _load(self, session_id=None):
        self.session_id = session_id
        self.is_new_session = False
        if not self.session_id:
            self.is_new_session = True
            self.session_id = self._generate_session_id()
        self._data = self.store[self.session_id] or dict()

    def _save(self):
        if not hasattr(self, "_killed"):
            self.store[self.session_id] = self._data
            if self.is_new_session:
                self.handler.set_cookie("session_id", self.session_id)
        else:
            self.handler.clear_cookie("session_id")

    def _generate_session_id(self):
        "Generate a 64 bytes string"
        session_id = "".join(uuid.uuid4().hex for i in xrange(2))
        return session_id

    def cleanup(self, timeout):
        self.store.cleanup(timeout)

    def kill(self):
        del self.store[self.session_id]
        self._killed = True


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

    def cleanup(self, timeout):
        raise NotImplementedError


class MySQLStore(Store):
    def __init__(self, db, table_name):
        self.db = db
        self.table = table_name

    def __contains__(self, key):
        c = self.db.cursor()
        sql = "SELECT * FROM " + self.table + " WHERE session_id = %s"
        c.execute(sql, (key, ))
        row = c.fetchone()
        c.close()
        return bool(row)

    def __getitem__(self, key):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        c = self.db.cursor()
        sql = "SELECT data FROM " + self.table + " WHERE session_id = %s"
        c.execute(sql, (key, ))
        row = c.fetchone()
        if row:
            data = row[0]
            sql = "UPDATE " + self.table + \
                  " SET atime = %s WHERE session_id = %s"
            c.execute(sql, (now, key))
            self.db.commit()
            c.close()
            return self.decode(data)

        c.close()

    def __setitem__(self, key, value):
        pickled = self.encode(value)
        c = self.db.cursor()
        if key in self:
            sql = "UPDATE " + self.table + \
                  " SET data = %s WHERE session_id = %s"
            c.execute(sql, (pickled, key))
        else:
            sql = "INSERT INTO " + self.table + \
                  " (session_id, data) VALUES (%s, %s)"
            c.execute(sql, (key, pickled))
        self.db.commit()
        c.close()

    def __delitem__(self, key):
        c = self.db.cursor()
        sql = "DELETE FROM " + self.table + " WHERE session_id = %s"
        c.execute(sql, (key, ))
        self.db.commit()
        c.close()

    def cleanup(self, timeout):
        timeout = datetime.timedelta(timeout / (24.0 * 60.0 * 60.0))
        last_allowed_time = datetime.datetime.now() - timeout
        last_allowed_time = last_allowed_time.strftime("%Y-%m-%d %H:%M:%S")

        c = self.db.cursor()
        sql = "DELETE FROM " + self.table + " WHERE atime < %s"
        c.execute(sql, (last_allowed_time, ))
        self.db.commit()
        c.close()


if __name__ == '__main__':
    from db import db
    session = Session(MySQLStore(db, "yagra_session"))
    session._load()
    # print session["name"], session["age"]
    session["name"] = "Cedric Porter"
    session["age"] = 22
    session._save()
