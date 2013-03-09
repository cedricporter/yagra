#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#

import web
import logging
from db import db
from base import RequestHandlerWithSession, authenticated
from template import *
import hashlib
import time


class UserHomeHandler(RequestHandlerWithSession):
    @authenticated
    def get(self):
        username = self.session["username"]

        c = db.cursor()
        c.execute("SELECT filename, upload_date FROM yagra_image, yagra_user WHERE user_login = %s AND user_id = ID", (username, ))

        html_string = html(
            head(
                title("Yagra")),
            body(
                "username: " + username,
                form(input(type="text", name="username"),
                     input(type="file", name="user_head"),
                     input(type="submit"),
                     action="/user/upload",
                     method="post",
                     enctype="multipart/form-data"),
                a("login", href="/accounts/login"),
                a("logout", href="/accounts/logout"),
                [[div(p(upload_date.ctime())),
                  img(src="/uploads/" + filename, width="100", height="100")]
                  for filename, upload_date in c.fetchall()],
                ))

        self.write(html_string)


def create_random_filename(filename):
    import random
    import string

    return time.strftime("%Y_%m_%d_%H_%M_%S_") + "".join(random.choice(string.letters) for i in xrange(10)) + filename


class UploadImageHandler(RequestHandlerWithSession):
    @authenticated
    def post(self):
        username = self.session["username"]
        user_head = self.get_argument("user_head")

        upload_filename = self.request.files["user_head"].filename

        filename = create_random_filename(upload_filename)

        full_filename = "uploads/" + filename

        logging.info("Writing file to %s" % (filename, ))
        with open(full_filename, "wb") as out:
            out.write(user_head)

        # 检查用户是否存在
        cursor = db.cursor()
        cursor.execute("SELECT ID, user_email FROM yagra_user WHERE user_login = %s", (username, ))
        row = cursor.fetchone()
        if row:
            user_id, user_email = row
            m = hashlib.md5()
            m.update(user_email)
            email_md5 = m.hexdigest()

            # 插入图片信息到数据库中
            cursor.execute("INSERT INTO yagra_image (user_id, filename, upload_date) VALUES (%s, %s, %s)",
                           (str(user_id), filename, time.strftime('%Y-%m-%d %H:%M:%S')))
            image_id = cursor.lastrowid

            # 判断用户是否已经有默认头像，没有则设置默认头像
            cursor.execute("SELECT * FROM yagra_user_head WHERE user_email_md5 = %s", (email_md5, ))
            row = cursor.fetchone()
            if not row:
                logging.info("Insert into db. Filename %s, image_id: %d, user_id: %d" % (filename, image_id, user_id))
                cursor.execute("INSERT INTO yagra_user_head (user_id, image_id, user_email_md5) VALUES (%s, %s, %s)",
                               (user_id, image_id, email_md5))
            db.commit()

        self.set_header("Content-Type", "text/plain")
        self.write(str(self.request.files["user_head"].type))

        self.redirect("/user")
