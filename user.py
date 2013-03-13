#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#

import logging
from db import db
from base import RequestHandlerWithSession, authenticated
from yagra_template import Template
import hashlib
import time
from util import purge_filename


class UserHomeHandler(RequestHandlerWithSession):
    "用户管理页面"
    @authenticated
    def get(self):
        username = self.session["username"]
        email_md5 = self.session["email_md5"]
        csrf_token = self.session["_csrf_token"]

        c = db.cursor()
        c.execute("""
        SELECT
            filename, i.image_id, i.upload_date, user_email_md5
        FROM
            yagra_user AS u,
            yagra_image AS i
                LEFT JOIN
            yagra_user_head AS h ON i.image_id = h.image_id
        WHERE
            u.ID = i.user_id AND u.user_login = %s
        """, (username, ))

        html_string = Template.render("userhome",
                                      username,
                                      email_md5,
                                      imgs=c.fetchall(),
                                      csrf_token=csrf_token)
        self.write(html_string)


def create_random_filename(filename):
    import random
    import string

    filename = purge_filename(filename)

    new_filename = time.strftime("%Y_%m_%d_%H_%M_%S_")
    new_filename += "".join(random.choice(string.letters) for i in xrange(10))
    new_filename += filename

    return new_filename


class UploadImageHandler(RequestHandlerWithSession):
    "用户上传头像"
    @authenticated
    def post(self):
        user_head = self.get_argument("user_head")
        csrf_token = self.get_argument("csrf_token")

        if csrf_token != self.session["_csrf_token"]:
            self.set_status(403)
            return

        username = self.session["username"]

        upload_filename = unicode(self.request.files["user_head"].filename,
                                  encoding="utf-8")

        filename = create_random_filename(username + "_" + upload_filename)

        full_filename = "uploads/" + filename

        logging.info("Writing file to %s" % (filename, ))
        with open(full_filename, "wb") as out:
            out.write(user_head)

        # 检查用户是否存在
        cursor = db.cursor()
        cursor.execute("""
        SELECT ID, user_email
        FROM yagra_user
        WHERE user_login = %s""", (username, ))
        row = cursor.fetchone()
        if row:
            user_id, user_email = row
            m = hashlib.md5()
            m.update(user_email)
            email_md5 = m.hexdigest()

            # 插入图片信息到数据库中
            cursor.execute("""
            INSERT INTO yagra_image (user_id, filename, upload_date)
            VALUES (%s, %s, %s)""", (str(user_id),
                                     filename,
                                     time.strftime('%Y-%m-%d %H:%M:%S')))
            image_id = cursor.lastrowid

            # 判断用户是否已经有默认头像，没有则设置默认头像
            cursor.execute("""
            SELECT *
            FROM yagra_user_head
            WHERE user_email_md5 = %s""", (email_md5, ))
            row = cursor.fetchone()
            if not row:
                logging.info("Insert into db. Filename %s, "
                             "image_id: %d, "
                             "user_id: %d" % (filename, image_id, user_id))
                cursor.execute("""
                INSERT INTO yagra_user_head (user_id, image_id, user_email_md5)
                VALUES (%s, %s, %s)""", (user_id, image_id, email_md5))
            db.commit()

        self.redirect("/user")


class SetAvatarHandler(RequestHandlerWithSession):
    "选择头像"
    @authenticated
    def post(self):
        new_image_id = self.get_argument("new_image_id")
        csrf_token = self.get_argument("csrf_token")

        username = self.session["username"]
        user_id = self.session["id"]

        # check csrf
        if csrf_token != self.session["_csrf_token"]:
            self.set_status(403)
            return

        c = db.cursor()
        c.execute("""
        SELECT *
        FROM yagra_user, yagra_image
        WHERE ID = user_id AND user_login = %s AND image_id = %s
        """, (username, new_image_id))
        row = c.fetchone()
        if row:
            c.execute("""
            UPDATE yagra_user_head
            SET image_id = %s
            WHERE user_id = %s""", (new_image_id, user_id))
            # self.redirect("/user")
            self.write({"status": "OK"})
            return

        self.write({"status": "Failed",
                    "msg": "选择的图片不正确！"})
