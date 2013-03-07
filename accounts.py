#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#

import web
import logging
from db import db
import time
from base import RequestHandlerWithSession, authenticated
from template import *


class RegisterHandler(web.RequestHandler):
    def get(self):
        html_string = html(
            head(title("注册")),
            body(
                form("Username:", input(type="text", name="username"),
                     "Email:", input(type="text", name="email"),
                     "Password", input(type="password", name="password"),
                     "Password(again)", input(type="password", name="password-again"),
                     input(type="submit"),
                     action="/accounts/new",
                     method="post"),
                ))
        self.write(html_string)


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


class AccountHandler(RequestHandlerWithSession):
    @authenticated
    def get(self):
        cursor = db.cursor()
        cursor.execute("SELECT user_email, user_login FROM yagra_user")
        for row in cursor.fetchall():
            email, name = row
            self.write("%s: %s<br/>" % (name, email))


class LoginHandler(RequestHandlerWithSession):
    def get(self):
        html_string = html(
            body(
                form(
                    input(type="text", name="username"),
                    input(type="password", name="password"),
                    input(type="submit"),
                    action="/accounts/login",
                    method="post")))

        if self.session.get("login"):
            self.redirect("/")
        else:
            self.write(html_string)

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
        self.clear_all_cookies()
        self.redirect(self.get_login_url())
