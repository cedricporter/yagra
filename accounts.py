#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#

import web
from db import db
import time


class RegisterHandler(web.RequestHandler):
    def get(self):
        html = """
<html>
  <title>
    注册
  </title>
  <body>
    <form action="/accounts/new" method="post">
      Username: <input type="text" name="username"/>
      Email: <input type="text" name="email"/>
      Password: <input type="password" name="password"/>
      Password(again): <input type="password" name="password-again"/>
      <input type="submit"/>
    </form>
  </body>
</html>
        """
        self.write(html)


class NewAccountHandler(web.RequestHandler):
    def post(self):
        username = self.get_argument("username")
        email = self.get_argument("email")

        # 记得加salt加密！！
        pwd = self.get_argument("password")
        pwd2 = self.get_argument("password-again")

        if pwd != pwd2:
            self.write("two password not matched")
            return                        # XXX

        cursor = db.cursor()
        cursor.execute("SELECT ID FROM yagra_user WHERE user_email = %s", (email, ))
        if cursor.fetchone():
            self.write("email %s registered!" % email)
            return

        cursor.execute("SELECT ID FROM yagra_user WHERE user_login = %s", (username, ))
        if cursor.fetchone():
            self.write("username %s registered!" % username)
            return

        cursor.execute("""
        INSERT INTO `yagra`.`yagra_user`
        (
        `user_login`,
        `user_passwd`,
        `display_name`,
        `user_email`,
        `user_register`,
        `user_status`)
        VALUES
        (%s, %s, %s, %s, %s, %s)
        """, (username, pwd, username,
              email,
              time.strftime('%Y-%m-%d %H:%M:%S'), str(1)))
        db.commit()

        self.write("Username: %s registered success!" % username)


class AccountHandler(web.RequestHandler):
    def get(self):
        cursor = db.cursor()
        cursor.execute("SELECT user_email, user_login FROM yagra_user")
        for row in cursor.fetchall():
            email, name = row
            self.write("%s: %s<br/>" % (name, email))


class LoginHandler(web.RequestHandler):
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
        self.write(html)

    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")

        cursor = db.cursor()
        cursor.execute("SELECT ID FROM yagra_user WHERE user_login = %s AND user_passwd = %s", (username, password))
        if cursor.fetchone():
            self.set_cookie("session_id", "123456")
            return self.redirect("/")
        self.write("Error")
