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
import mimetypes
import os


logging.getLogger().setLevel(logging.INFO)


class MainHandler(MyBaseRequestHandler):
    def get(self):
        self.write("xxx" * 100)


class ImageWallHandler(MyBaseRequestHandler):
    "Show all head image"
    def get(self):
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
    def get(self, username):
        c = db.cursor()
        c.execute("SELECT user_email FROM yagra_user WHERE user_login = %s", (username, ))
        row = c.fetchone()
        if row:
            self.write(row[0])


class AvatarHandler(MyBaseRequestHandler):
    def get(self, email_hash):
        c = db.cursor()
        c.execute("SELECT filename FROM yagra_user, yagra_image WHERE user_id = id AND user_email = %s", (email_hash, ))
        row = c.fetchall()
        if row:
            filename = row[-1][0]
            logging.info(row)
            with open("uploads/" + filename, "rb") as f:
                logging.info(f)
                img = f.read()
                length = len(img)
                self.write(img)
                logging.info("Length: %d" % length)
                self.set_header("Content-Length", length)

            mime = mimetypes.types_map.get(os.path.splitext(filename)[-1], "image/jpeg")
            self.set_header("Content-Type", mime)
        else:
            self.write(email_hash)
            self.write(self.get_argument("name", ""))
            self.set_status(404)


def main():
    app = web.Application([
        (r"/", MainHandler),
        # (r"/(.*?)", EnvironHandler),
        (r"/echo", EchoHandler),
        (r"/env", EnvironHandler),
        (r"/user", "user.UserHomeHandler"),
        (r"/avatar/(.*)", AvatarHandler),
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
