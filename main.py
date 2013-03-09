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


class ProfileHandler(MyBaseRequestHandler):
    def get(self, username):
        if not username:
            self.write("fuck")
            return

        c = db.cursor()
        c.execute("""
        SELECT user_email, user_email_md5
        FROM yagra_user as u, yagra_user_head as h
        WHERE u.ID = h.user_id  AND user_login = %s""", (username, ))
        row = c.fetchone()
        if row:
            email, email_md5 = row
            html_string = html(
                body(email,
                     img(src="/avatar/" + email_md5, width="400", height="400")))
            self.write(html_string)
        else:
            self.redirect("/")
            return


class AvatarHandler(MyBaseRequestHandler):
    def get(self, email_md5):
        c = db.cursor()
        c.execute("""
        SELECT filename
        FROM yagra_image as img, yagra_user_head as head
        WHERE img.user_id = head.user_id AND user_email_md5 = %s""",
                  (email_md5, ))
        row = c.fetchone()
        if row:
            filename = row[0]
            logging.info("Avatar Filename: " + str(row))
            with open("uploads/" + filename, "rb") as f:
                img = f.read()
                length = len(img)
                self.write(img)
                logging.info("Reading %s, Length: %d" % (str(f), length))
                self.set_header("Content-Length", length)

            mime = mimetypes.types_map.get(os.path.splitext(filename)[-1], "image/jpeg")
            self.set_header("Content-Type", mime)
        else:
            self.set_status(404)


def main():
    app = web.Application([
        (r"/", MainHandler),
        (r"/(.+)", ProfileHandler),
        (r"/user", "user.UserHomeHandler"),
        (r"/avatar/(.+)", AvatarHandler),
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
