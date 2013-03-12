#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#

"""
这个是yagra的所有页面的模板，使用的是我的微型Lion引擎进行生成。
"""

from template import *


class Template(object):
    "所有页面的模板，基本和其他的模板引擎使用方法一致"
    @staticmethod
    def render(template_name, *args, **kwargs):
        template_gen = getattr(Template, template_name)
        return template_gen(*args, **kwargs)

    @staticmethod
    def basic_frame(body_html, button_name="", button_url="",
                    title_name="Yagra", heads=""):
        "网站基本框架"
        return html(
            head(title(title_name),
                 link(k(rel="stylesheet", type="text/css", href="/style.css")),
                 script(k(src="/jquery-1.9.1.min.js")),
                 heads),
            body(
                div(k(id="wrap"),
                    # header
                    div(k(id="header"),
                        div(k(Class="middle"),
                            div(k(id="login"),
                                div(k(id="loginContainer"),
                                    a(k(id="login-trigger", Class="my-account-trigger", href=button_url),
                                      span(button_name)),
                                      )))),
                    # main
                    div(k(id="main"),
                        div(k(Class="middle"),
                            div(k(Class="box"),
                                div(k(id="content", Class="profile"),
                                    # body
                                    body_html
                                    )))))))

    @staticmethod
    def homepage(button_name, button_url):
        body_html = flatten((h1("欢迎来到Yagra"),
                             a(k(href="/accounts/signup"), "注册")))
        html_string = Template.basic_frame(body_html,
                                           button_name=button_name,
                                           button_url=button_url)
        return html_string

    @staticmethod
    def signup():
        "注册页面"
        body_html = flatten((h2("创建用户！开始您的旅程！"),
                             p("选择您的用户名，记得仅仅只能包含小些字母和数字哦！"),
                             form(k(id="create-account-form", action="/accounts/new", method="post"),
                                  # username
                                  p(label("用户名："),
                                    input(k(type="text", id="setusername", name="username", Class="text")),
                                    input(k(type="button", Class="button", id="checkbutton", value="检查")),
                                    span(k(id="username-status", style="display: none"))),
                                  p(k(Class="label_align"),
                                    "用户名将是您的永久身份象征。"),
                                  # email
                                  p(label("邮箱"),
                                    input(k(type="text", name="email", id="email", Class="text")),
                                    span(k(id="email-status", style="display: none"))),
                                  # Password
                                  p(label("密码"),
                                    input(k(type="password", name="password", id="pass1", Class="text"))),
                                  p(label("再次输入密码"),
                                    input(k(type="password", name="password-again", id="pass2", Class="text")),
                                    span(k(id="password-status", style="display: none"))),
                                  # submit
                                  p(k(Class="label_align"),
                                    input(k(name="commit", type="submit", value="注册", Class="button", id="submit"))))))
        heads = script(k(src="/signup.js"))
        html_string = Template.basic_frame(body_html, heads=heads)
        return html_string

    @staticmethod
    def login():
        "登陆页面"
        form_string = form(k(id="create-account-form", action="/accounts/login", method="post"),
                           h2("登录Yagra"),
                           p(label("用户名或者邮箱"),
                             input(k(type="text", name="username", Class="text")),
                           p(label("密码"),
                             input(k(type="password", name="password", Class="text"))),
                           p(k(Class="label_align"),
                             input(k(name="commit", type="submit", value="登录", Class="button", id="submit")))))
        html_string = Template.basic_frame(form_string, button_url="/", button_name="首页")
        return html_string

    @staticmethod
    def imagewall(imgs):
        "照片墙"
        html_string = html(
            [[div(p(upload_date.ctime())),
              img(k(src="/uploads/" + filename))]
              for filename, upload_date in imgs])
        return html_string

    @staticmethod
    def profile(email, img_src):
        "用户个人公共主页"
        body_html = img(k(src=img_src, width="400", height="400"))
        html_string = Template.basic_frame(body_html, "")
        return html_string

    @staticmethod
    def userhome(username, email_md5, imgs, csrf_token):
        "用户配置页面"
        body_html = utf8_join_flatten(
            (h1(u"管理Yagra头像"),
             p("欢迎您，" + utf8(username)),
             img(k(src="/avatar/" + email_md5, width="300", height="300")),
             # 上传表单
             h3("上传头像"),
             form(k(action="/user/upload", method="post", enctype="multipart/form-data"),
                  p(label("文件："), input(k(type="file", name="user_head"))),
                  input(k(type="hidden", id="csrf_token", name="csrf_token", value=csrf_token)),
                  p(k(Class="label_align"),
                    input(k(type="submit", Class="button")))),
             # 用户头像列表
             h3("点选下方图片应用图片"),
             div(k(id="gravatar_list"),
                 div(k(Class="gravatars"),
                     [div(k(Class="grav"), div(k(id="img-id-" + str(image_id), Class="gravatar " + ("selected" if email_md5 else "")),
                                               img(k(src="/uploads/" + filename, title=upload_date.ctime(), alt=upload_date.ctime(), width="100", height="100"))))
                                               for filename, image_id, upload_date, email_md5 in imgs]))))

        heads = script(k(src="/user.js"))
        html_string = Template.basic_frame(body_html, button_name="退出", button_url="/accounts/logout", heads=heads)
        return html_string

    @staticmethod
    def error(msg):
        "错误页面"
        return html(
            head(title("错误")),
            body(
                "遇到了错误！",
                br(),
                msg))
