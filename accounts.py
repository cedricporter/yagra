#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#

import web
import logging
from db import db
import time
from base import RequestHandlerWithSession, authenticated
import re
from cgi import escape
from util import hash_password
from yagra_template import Template


NOT_USER_PATTERN = re.compile("[^a-zA-Z0-9]")
EMAIL_PATTERN = r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-])*\.[a-zA-Z]{2,4}$"


class RegisterHandler(web.RequestHandler):
    def get(self):
        html_string = Template.render("signup")
        self.write(html_string)


class NewAccountHandler(web.RequestHandler):
    def assure_input_valid(self):
        """检查用户名、邮箱是否合法，返回小写的用户名、邮箱以及密码

        return None or (username_lower, pwd, email_lower)
        """
        self.set_status(403)

        # 检查用户名
        username = self.get_argument("username")
        if NOT_USER_PATTERN.search(username):
            html_string = Template.render("error",
                                          "username %s is not valid" % (escape(username), ))
            self.write(html_string)
            return
        email = self.get_argument("email")

        # 检查密码
        pwd = self.get_argument("password")
        pwd2 = self.get_argument("password-again")

        if pwd != pwd2:
            html_string = Template.render("error",
                                          "two password not matched")
            self.write(html_string)
            return                        # XXX

        # 检查email
        if not re.match(EMAIL_PATTERN, email):
            html_string = Template.render("error",
                                          "email: %s is not valid." % escape(email))
            self.write(html_string)
            return

        cursor = db.cursor()
        email_lower = email.lower()
        cursor.execute("SELECT ID FROM yagra_user WHERE user_email = %s", (email_lower, ))
        if cursor.fetchone():
            html_string = Template.render("error",
                                          "email %s registered!" % escape(email))
            self.write(html_string)
            return

        username_lower = username.lower()
        cursor.execute("SELECT ID FROM yagra_user WHERE user_login = %s", (username_lower, ))
        if cursor.fetchone():
            html_string = Template.render("error",
                                          "username %s registered!" % escape(username))
            self.write(html_string)
            return

        self.set_status(200)

        return username_lower, pwd, email_lower

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
        html_string = Template.render("login")

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
