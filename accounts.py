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
import re
from cgi import escape
from util import hash_password


not_user_pattern = re.compile("[^a-zA-Z0-9]")


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
    def assure_input_valid(self):
        # 检查用户名
        username = self.get_argument("username")
        if not_user_pattern.search(username):
            self.write("username %s is not valid" % (escape(username), ))
            self.set_status(403)
            return
        email = self.get_argument("email")

        # 检查密码
        pwd = self.get_argument("password")
        pwd2 = self.get_argument("password-again")

        if pwd != pwd2:
            self.write("two password not matched")
            return                        # XXX

        # 检查email
        cursor = db.cursor()
        cursor.execute("SELECT ID FROM yagra_user WHERE user_email = %s", (email, ))
        if cursor.fetchone():
            self.write("email %s registered!" % escape(email))
            self.set_status(403)
            return

        cursor.execute("SELECT ID FROM yagra_user WHERE user_login = %s", (username, ))
        if cursor.fetchone():
            self.write("username %s registered!" % escape(username))
            self.set_status(403)
            return

        return username, pwd, email

    def post(self):
        cursor = db.cursor()

        data = self.assure_input_valid()
        if not data:
            return
        username, pwd, email = data

        hash_pwd = hash_password(pwd)

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
        """, (username, hash_pwd, username,
              email,
              time.strftime('%Y-%m-%d %H:%M:%S'), str(1)))
        db.commit()

        self.write("Username: %s registered success!" % escape(username))


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
            self.redirect("/user")
        else:
            self.session.kill()
            self.write(html_string)

    def post(self):
        username = self.get_argument("username")
        pwd = self.get_argument("password")
        password = hash_password(pwd)

        cursor = db.cursor()
        cursor.execute("SELECT ID FROM yagra_user WHERE user_login = %s AND user_passwd = %s", (username, password))
        row = cursor.fetchone()
        if row:
            logging.info(row)
            self.session["login"] = True
            self.session["username"] = username
            self.set_cookie("session_id", self.session.session_id)
            return self.redirect("/user")
        self.write("Error")


class LogoutHandler(RequestHandlerWithSession):
    def get(self):
        self.clear_all_cookies()
        self.session.kill()
        self.redirect(self.get_login_url())
