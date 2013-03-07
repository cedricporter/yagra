#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#

import cgitb
cgitb.enable()

import web
import logging
from db import db
from base import MyBaseRequestHandler, RequestHandlerWithSession, authenticated
from template import *


logging.getLogger().setLevel(logging.INFO)


class MainHandler(RequestHandlerWithSession):
    def get(self):
        self.write("Home")


class ImageWallHandler(MyBaseRequestHandler):
    "Show all head image"
    def get(self):
        imgs = ""
        c = db.cursor()
        c.execute("SELECT filename, upload_date FROM yagra_image")

        html_string = html(
            [[div(p(upload_date.ctime())),
              img(src="/uploads/" + filename)]
              for filename, upload_date in c.fetchall()])

        self.write(html_string)


class EchoHandler(RequestHandlerWithSession):
    def get(self):
        self.write(str(self.session.get("username")))


class EnvironHandler(MyBaseRequestHandler):
    def get(self):
        import os
        self.set_header("Content-Type", "text/plain")
        self.write(str(os.environ))
        self.write("-" * 500)
        self.write(str(self.cookies))


def main():
    app = web.Application([
        (r"/", MainHandler),
        (r"/echo", EchoHandler),
        (r"/env", EnvironHandler),
        (r"/user", "user.UserHomeHandler"),
        (r"/user/upload", "user.UploadImageHandler"),
        (r"/accounts/?", "accounts.AccountHandler"),
        (r"/accounts/signup/?", "accounts.RegisterHandler"),
        (r"/accounts/new", "accounts.NewAccountHandler"),
        (r"/accounts/login", "accounts.LoginHandler"),
        (r"/accounts/logout", "accounts.LogoutHandler"),
        (r"/imagewall", ImageWallHandler),
    ])
    app.cgi_run()


if __name__ == '__main__':
    main()
