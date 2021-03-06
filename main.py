#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#

import cgitb
cgitb.enable()

from base import MyBaseRequestHandler, RequestHandlerWithSession
from db import db
from yagra_template import Template
from everet.util import yagra_check_username_valid, yagra_check_email_valid
import logging
import mimetypes
import os
import everet.web
import hashlib


logging.getLogger().setLevel(logging.INFO)


class MainHandler(RequestHandlerWithSession):
    def get(self):
        if self.session.get("login"):
            html_string = Template.render("homepage",
                                          button_name="我的账户",
                                          button_url="/user")
        else:
            html_string = Template.render("homepage",
                                          button_name="登录",
                                          button_url="/accounts/login")

        self.write(html_string)


class ImageWallHandler(MyBaseRequestHandler):
    "Show all head image"
    def get(self):
        c = db.cursor()
        c.execute("SELECT filename, upload_date FROM yagra_image")

        html_string = Template.render("imagewall", c.fetchall())
        self.write(html_string)


class ProfileHandler(MyBaseRequestHandler):
    def get(self, username):

        c = db.cursor()
        c.execute("""
        SELECT user_email, user_email_md5
        FROM yagra_user LEFT JOIN yagra_user_head ON ID = user_id
        WHERE user_login = %s""", (username, ))
        row = c.fetchone()
        logging.info("ProfileHandler username: " + username + " " + str(row))
        if row:
            email, email_md5 = row
            html_string = Template.render("profile",
                                          username,
                                          email,
                                          "/avatar/" + str(email_md5))
            self.write(html_string)
        else:
            self.redirect("/")
            return


class AvatarHandler(MyBaseRequestHandler):
    """头像API支持

    自动支持etag，这里的etag通过图片文件名hash，而不是通过图片内容进行hash。
    这个是建立在所有的图片都有唯一的命名的基础。
    """
    def get(self, email_md5):
        c = db.cursor()
        c.execute("""
        SELECT filename
        FROM yagra_image as img, yagra_user_head as head
        WHERE img.image_id = head.image_id AND user_email_md5 = %s""",
                  (email_md5, ))
        row = c.fetchone()
        if row:
            filename = row[0]
            logging.info("Avatar Handler " + str(row) + " " + filename)
            full_filename = "uploads/" + filename
            logging.info("Avatar Filename: " + str(row))
        else:
            full_filename = "static/default.jpg"

        # ETags 支持
        etag = self._compute_etag(full_filename)
        self.set_header("ETag", etag)

        inm = self.request.headers.get("If-None-Match")
        if inm and inm == etag:
            self.set_status(304)
            return

        with open(full_filename, "rb") as f:
            img = f.read()
            length = len(img)
            self.write(img)
            logging.info("Reading %s, Length: %d" % (str(f), length))
            self.set_header("Content-Length", length)

        mime = mimetypes.types_map.get(os.path.splitext(full_filename)[-1],
                                       "image/jpeg")
        self.set_header("Content-Type", mime)
        self.set_header("Cache-Control", "max-age=300")

    def _compute_etag(self, filename):
        "根据文件名计算etag"
        hasher = hashlib.sha1()
        hasher.update(filename)
        return '"%s"' % hasher.hexdigest()


class AjaxValidateHandler(MyBaseRequestHandler):
    def post(self):
        action = self.get_argument("action")

        if action == "check_username":
            self.check_username()
        elif action == "check_email":
            self.check_email()

    def check_email(self):
        email = self.get_argument("email").lower()

        if not yagra_check_email_valid(email):
            self.write({"status": "Failed",
                        "msg": "邮箱格式不正确！"})
            return

        c = db.cursor()
        c.execute("SELECT ID FROM yagra_user WHERE user_email = %s",
                  (email, ))
        row = c.fetchone()
        if row:
            self.write({"status": "Failed",
                        "msg": "您输入的邮箱已经注册过了！"})
            return

        self.write({"status": "OK",
                    "msg": "OK"})

    def check_username(self):
        "检查用户名是否合法"
        username = self.get_argument("username")

        if not yagra_check_username_valid(username):
            self.write({"status": "Failed",
                        "msg": "用户名包含不合法字符！请仅选用小写字母和数字。"})
            return

        c = db.cursor()
        c.execute("""
        SELECT ID
        FROM yagra_user
        WHERE user_login = %s""", (username, ))
        row = c.fetchone()
        if row:
            self.write({"status": "Failed",
                        "msg": "用户已经存在"})
        else:
            self.write({"status": "OK",
                        "msg": "用户名合法！"})


def main():
    app = everet.web.Application([
        (r"/", MainHandler),
        (r"/user/?", "user.UserHomeHandler"),
        (r"/avatar/(.+)", AvatarHandler),
        (r"/user/upload", "user.UploadImageHandler"),
        (r"/accounts/?", "accounts.AccountHandler"),
        (r"/accounts/signup/?", "accounts.RegisterHandler"),
        (r"/accounts/new", "accounts.NewAccountHandler"),
        (r"/accounts/login", "accounts.LoginHandler"),
        (r"/accounts/logout", "accounts.LogoutHandler"),
        (r"/imagewall", ImageWallHandler),
        (r"/ajax-validate", AjaxValidateHandler),
        (r"/user/set_avatar", "user.SetAvatarHandler"),
        (r"/(.+)", ProfileHandler),
    ])
    app.cgi_run()


if __name__ == '__main__':
    main()
