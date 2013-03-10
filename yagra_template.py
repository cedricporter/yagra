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
    def basic_frame(body_html, button_name="", button_url="", title_name="Yagra"):
        "网站基本框架"
        return html(
            head(title(title_name),
                 link(k(rel="stylesheet", type="text/css", href="/style.css"))),
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
        body_html = "欢迎"
        html_string = Template.basic_frame(body_html,
                                           button_name=button_name,
                                           button_url=button_url)
        return html_string

    @staticmethod
    def signup():
        "注册页面"
        body_html = flatten((h2("注册新用户"), p(),
                             form(k(id="create-account-form", action="/accounts/new", method="post"),
                                  # username
                                  p(label("用户名："),
                                    input(k(type="text", id="setusername", name="username", Class="text")),
                                    input(k(type="button", Class="button", id="checkbutton", value="检查")),
                                    span(k(id="username-status", style="display: none", Class="sayno"),
                                         br(), "无效用户名")),
                                  p(k(Class="label_align"),
                                    "用户名将是您的永久身份象征。"),
                                  # email
                                  p(label("邮箱"),
                                    input(k(type="text", name="email", id="email", Class="text"))),
                                  # Password
                                  p(label("密码"),
                                    input(k(type="password", name="password", id="pass1", Class="text"))),
                                  p(label("再次输入密码"),
                                    input(k(type="password", name="password-again", id="pass2", Class="text"))),
                                  # submit
                                  p(k(Class="label_align"),
                                    input(k(name="commit", type="submit", value="注册", Class="button", id="submit"))))))
        html_string = Template.basic_frame(body_html)
        return html_string

    @staticmethod
    def login():
        "登陆页面"
        form_string = form(k(id="create-account-form", action="/accounts/login", method="post"),
                           h2("登录Yagra"), p(),
                           p(label("用户名或者邮箱"),
                             input(k(type="text", name="username", Class="text")),
                           p(label("密码"),
                             input(k(type="password", name="password", Class="text"))),
                           p(k(Class="label_align"),
                             input(k(name="commit", type="submit", value="登录", Class="button", id="submit")))))
        html_string = Template.basic_frame(form_string)
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
    def userhome(username, imgs):
        "用户配置页面"
        body_html = "".join(
            flatten(("username: " + username,
                     form(k(action="/user/upload", method="post", enctype="multipart/form-data"),
                          input(k(type="text", name="username")),
                          input(k(type="file", name="user_head")),
                          input(k(type="submit"))),
                          a(k(href="/accounts/login"), "login"),
                          a(k(href="/accounts/logout"), "logout"),
                          [[div(p(upload_date.ctime())),
                            img(k(src="/uploads/" + filename, width="100", height="100"))]
                            for filename, upload_date in imgs])))
        html_string = Template.basic_frame(body_html, button_name="退出", button_url="/accounts/logout")
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
