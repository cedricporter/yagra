#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#

import cgitb
cgitb.enable()

import web
import logging
from db import db
from session import Session, MySQLStore


logging.getLogger().setLevel(logging.INFO)


class RequestHandlerWithSession(web.RequestHandler):
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
  </body>
</html>
        """ % info
        self.write(html)


class UserHandler(web.RequestHandler):
    def post(self):
        user_head = self.get_argument("user_head")

        import random
        import string
        import time

        upload_filename = self.request.files["user_head"].filename

        filename = time.strftime("%Y_%m_%d_%H_%M_%S_") + "".join(random.choice(string.letters) for i in xrange(10)) + upload_filename

        full_filename = "uploads/" + filename

        with open(full_filename, "wb") as out:
            out.write(user_head)

        cursor = db.cursor()
        if cursor.execute("SELECT ID FROM yagra_user WHERE user_email = %s", ("uoehBkgTXE@gmail.com", )):
            row = cursor.fetchone()
            if row:
                user_id = row[0]
                cursor.execute("INSERT INTO yagra_image (user_id, filename, upload_date) VALUES (%s, %s, %s)",
                               (str(user_id), filename, time.strftime('%Y-%m-%d %H:%M:%S')))
                db.commit()

        self.set_header("Content-Type", "text/plain")
        self.write(str(self.request.files["user_head"].type))

        self.redirect("/")


class EchoHandler(web.RequestHandler):
    def get(self):
        import cgi
        self.write(str(cgi.FieldStorage()))
        self.set_cookie("Name", "Stupid ET")


class EnvironHandler(web.RequestHandler):
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
    ])
    app.cgi_run()


if __name__ == '__main__':
    main()
