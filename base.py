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
    "验证是否登录，需要session支持"
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        # hack: check if there's session id
        session_id = self.cookies.get("session_id")
        url = self.get_login_url() or "/"

        if not session_id:
            self.redirect(url)
            return

        # 无效session，跳转到登录页面，删除session
        if not self.session.get("login"):
            self.redirect(url)
            self.session.kill()
            return
        return method(self, *args, **kwargs)
    return wrapper


class MyBaseRequestHandler(web.RequestHandler):
    def get_login_url(self):
        return "/accounts/login"


class RequestHandlerWithSession(MyBaseRequestHandler):
    """提供session支持的handler

    如果有需要session支持的handler可以继承这个handler。
    一旦继承这个handler，在访问session属性时，将会自动设置cookie: session_id用于跟踪session。
    """
    @property
    def session(self):
        if not hasattr(self, "_session"):
            self._session = Session(MySQLStore(db, "yagra_session"), self)
            session_id = self.cookies.get("session_id")
            if session_id:
                session_id = session_id.value
                self._session._load(session_id)
            else:
                self._session._load()
        return self._session

    def finalize(self):
        if hasattr(self, "_session"):
            self._session._save()
            self._session.cleanup(86400 * 1)   # a day
