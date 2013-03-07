#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#

import web
import logging
from db import db
from base import RequestHandlerWithSession, authenticated
from template import *


class UserHomeHandler(RequestHandlerWithSession):
    @authenticated
    def get(self):
        username = self.session["username"]
        info = "username: " + username

        imgs = ""

        c = db.cursor()
        c.execute("SELECT filename, upload_date FROM yagra_image, yagra_user WHERE user_login = %s AND user_id = ID", (username, ))
        for filename, upload_date in c.fetchall():
            imgs += '<div><p>' + upload_date.ctime() + '</p>'
            imgs += '<img width="80" height="80" src="/uploads/' + filename + '"/>'
            imgs += '</div>'
        c.close()

        html_string = html(
            head(
                title("Yagra")),
            body(
                info, imgs,
                form(input(type="text", name="username"),
                     input(type="file", name="user_head"),
                     input(type="submit"),
                     action="/user/upload",
                     method="post",
                     enctype="multipart/form-data"),
                a("login", href="/accounts/login"),
                a("logout", href="/accounts/logout"),
                ))

        self.write(html_string)


class UploadImageHandler(RequestHandlerWithSession):
    @authenticated
    def post(self):
        username = self.session["username"]
        user_head = self.get_argument("user_head")

        import random
        import string
        import time

        upload_filename = self.request.files["user_head"].filename

        filename = time.strftime("%Y_%m_%d_%H_%M_%S_") + "".join(random.choice(string.letters) for i in xrange(10)) + upload_filename

        full_filename = "uploads/" + filename

        logging.info("Writing file to %s" % (filename, ))
        with open(full_filename, "wb") as out:
            out.write(user_head)

        cursor = db.cursor()
        cursor.execute("SELECT ID FROM yagra_user WHERE user_login = %s", (username, ))
        row = cursor.fetchone()
        if row:
            user_id = row[0]
            logging.info("Insert into db %s" % (filename, ))
            cursor.execute("INSERT INTO yagra_image (user_id, filename, upload_date) VALUES (%s, %s, %s)",
                           (str(user_id), filename, time.strftime('%Y-%m-%d %H:%M:%S')))
            db.commit()

        self.set_header("Content-Type", "text/plain")
        self.write(str(self.request.files["user_head"].type))

        self.redirect("/user")
