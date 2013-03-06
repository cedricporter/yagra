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


logging.getLogger().setLevel(logging.INFO)


class MainHandler(RequestHandlerWithSession):
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
    <form action="/user" method="post" enctype="multipart/form-data">
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


class UserHandler(RequestHandlerWithSession):
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


class ImageWallHandler(MyBaseRequestHandler):
    "Show all head image"
    def get(self):
        imgs = ""
        c = db.cursor()
        c.execute("SELECT filename, upload_date FROM yagra_image")
        for filename, upload_date in c.fetchall():
            imgs += '<div><p>' + upload_date.ctime() + '</p>'
            imgs += '<img src="/uploads/' + filename + '"/>'
            imgs += '</div>'

        html = """
        <body>
          %s
        </body>
        """ % imgs

        self.write(html)


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


class LoginHandler(RequestHandlerWithSession):
    def get(self):
        html = """
<html>
  <body>
    <form action="/accounts/login" method="post">
      <input type="text" name="username">
      <input type="password" name="password">
      <input type="submit">
    </form>
  </body>
</html>
        """
        if self.session.get("login"):
            self.redirect("/")
        else:
            self.write(html)

    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")

        cursor = db.cursor()
        cursor.execute("SELECT ID FROM yagra_user WHERE user_login = %s AND user_passwd = %s", (username, password))
        row = cursor.fetchone()
        if row:
            logging.info(row)
            self.session["login"] = True
            self.session["username"] = username
            self.set_cookie("session_id", self.session.session_id)
            return self.redirect("/")
        self.write("Error")


class LogoutHandler(RequestHandlerWithSession):
    def get(self):
        self.clear_cookie("session_id")
        self.redirect(self.get_login_url())


def main():
    app = web.Application([
        (r"/", MainHandler),
        (r"/echo", EchoHandler),
        (r"/user", UserHandler),
        (r"/env", EnvironHandler),
        (r"/accounts/?", "accounts.AccountHandler"),
        (r"/accounts/signup/?", "accounts.RegisterHandler"),
        (r"/accounts/new", "accounts.NewAccountHandler"),
        (r"/accounts/login", LoginHandler),
        (r"/accounts/logout", LogoutHandler),
        (r"/imagewall", ImageWallHandler),
    ])
    app.cgi_run()


if __name__ == '__main__':
    main()
