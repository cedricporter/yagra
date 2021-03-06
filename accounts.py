#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#

from base import RequestHandlerWithSession, authenticated
from cgi import escape
from db import db
from everet.util import hash_password, yagra_check_username_valid
from everet.util import yagra_check_email_valid, make_digest
from yagra_template import Template
import logging
import time
import everet.web
import hashlib
import uuid


class RegisterHandler(everet.web.RequestHandler):
    def get(self):
        html_string = Template.render("signup")
        self.write(html_string)


class NewAccountHandler(everet.web.RequestHandler):
    def assure_input_valid(self):
        """检查用户名、邮箱是否合法，返回小写的用户名、邮箱以及密码

        return None or (username_lower, pwd, email_lower)
        """
        self.set_status(403)

        # 检查用户名
        username = self.get_argument("username")
        if not yagra_check_username_valid(username):
            html_string = Template.render("error",
                                          "username %s is not valid" % (
                                              escape(username), ))
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
        if not yagra_check_email_valid(email):
            html_string = Template.render("error",
                                          "email: %s is not valid."
                                          % escape(email))
            self.write(html_string)
            return

        cursor = db.cursor()
        email_lower = email.lower()
        cursor.execute("""
        SELECT ID
        FROM yagra_user
        WHERE user_email = %s""", (email_lower, ))
        if cursor.fetchone():
            html_string = Template.render("error",
                                          "email %s registered!"
                                          % escape(email))
            self.write(html_string)
            return

        username_lower = username.lower()
        cursor.execute("""
        SELECT ID
        FROM yagra_user
        WHERE user_login = %s""", (username_lower, ))
        if cursor.fetchone():
            html_string = Template.render("error",
                                          "username %s registered!"
                                          % escape(username))
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

        # self.write("Username: %s registered success!" % escape(username))
        self.redirect("/accounts/login")


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

        sid = self.cookies.get("session_id")
        if not sid:
            self.write(html_string)
        elif self.session.get("login"):
            self.redirect("/user")
        else:                             # 无效session
            self.session.kill()
            self.write(html_string)

    def post(self):
        username_or_email = self.get_argument("username").lower()
        pwd = self.get_argument("password")
        password = hash_password(pwd)

        cursor = db.cursor()
        cursor.execute("""
        SELECT ID, user_login, user_email
        FROM yagra_user
        WHERE (user_login = %s
        OR user_email = %s) AND user_passwd = %s""",
                       (username_or_email, username_or_email, password))
        row = cursor.fetchone()
        if row:
            ID, username, email = row
            m = hashlib.md5()
            m.update(email)
            email_md5 = m.hexdigest()

            logging.info(row)
            self.session["login"] = True
            self.session["_csrf_token"] = make_digest(uuid.uuid4().get_hex())
            self.session["id"] = ID
            self.session["username"] = username
            self.session["email"] = email
            self.session["email_md5"] = email_md5
            self.set_cookie("session_id", self.session.session_id)
            self.redirect("/user")
            return

        # 登录失败
        html_string = Template.render("login", login_failed=True)
        self.write(html_string)


class LogoutHandler(RequestHandlerWithSession):
    def get(self):
        self.clear_all_cookies()
        self.session.kill()
        self.redirect(self.get_login_url())
