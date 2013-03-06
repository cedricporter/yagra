#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#

import functools
import web
import logging
from session import Session, MySQLStore
from db import db


def authenticated(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.session.get("login"):
            logging.info("Not logging")
            logging.info(self.session)

            url = self.get_login_url() or "/"
            self.redirect(url)
            return
        return method(self, *args, **kwargs)
    return wrapper


class MyBaseRequestHandler(web.RequestHandler):
    def get_login_url(self):
        return "/accounts/login"


class RequestHandlerWithSession(MyBaseRequestHandler):
    @property
    def session(self):
        if not hasattr(self, "_session"):
            self._session = Session(MySQLStore(db, "yagra_session"))
            session_id = self.cookies.get("session_id")
            if session_id:
                session_id = session_id.value
                self._session._load(session_id)
            else:
                self._session._load()
                session_id = self._session.session_id
                self.set_cookie("session_id", session_id)
        return self._session

    def finalize(self):
        if hasattr(self, "_session"):
            self._session._save()
