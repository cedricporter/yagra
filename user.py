#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#

import web
import logging
from db import db
from base import RequestHandlerWithSession, authenticated


class UserHomeHandler(RequestHandlerWithSession):
    @authenticated
    def get(self):
        if self.session.get("login"):
            info = "username: " + self.session["username"]
        else:
            info = ""
        html = """
<html>
  <head>
    <title>
      Yagra
    </title>
  </head>
  <body>
    %s
    <form action="/user/upload" method="post" enctype="multipart/form-data">
      <input type="text" name="username"/>
      <input type="file" name="user_head"/>
      <input type="submit"/>
    </form>
    <a href="/accounts/login">login</a>
    <a href="/accounts/logout">logout</a>
  </body>
</html>
        """ % info
        self.write(html)


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

        self.redirect("/")
