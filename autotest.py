#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#

"""
这个是针对Yagra的CGI自动测试。所有的测试通过设置os.environ环境变量以及sys.stdin来模拟Web Server的输入。
"""

import unittest
import main
import StringIO
import sys
import os
import re
import random
import string


PRINT_STDERR = True


def is_in(target_string, *args):
    return reduce(lambda x, y: x and y,
                  [bool(re.search(p, target_string)) for p in args])


def create_cgi_environ():
    cgi_environ = {'HTTP_COOKIE': '',
                   'REQUEST_URI': '/imagewall?name=cedricporter&age=22',
                   'SERVER_SOFTWARE': 'Apache/2.2.22 (Ubuntu)',
                   'SCRIPT_NAME': '/main.py',
                   'REQUEST_METHOD': 'GET',
                   'SERVER_PROTOCOL': 'HTTP/1.1',
                   'QUERY_STRING': '',
                   'HTTP_ACCEPT_CHARSET': 'UTF-8,*;q=0.5',
                   'HTTP_USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.17 (KHTML, like Gecko) Ubuntu Chromium/24.0.1312.56 Chrome/24.0.1312.56 Safari/537.17',
                   'HTTP_CONNECTION': 'keep-alive',
                   'SERVER_NAME': 'localhost',
                   'REMOTE_ADDR': '127.0.0.1',
                   'SERVER_PORT': '80',
                   'SERVER_ADDR': '127.0.0.1',
                   'DOCUMENT_ROOT': '/home/cedricporter/projects/yagra',
                   'SCRIPT_FILENAME': '/home/cedricporter/projects/yagra/main.py',
                   'HTTP_HOST': 'localhost',
                   'HTTP_CACHE_CONTROL': 'max-age=0',
                   'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'GATEWAY_INTERFACE': 'CGI/1.1',
                   'REMOTE_PORT': '51742',
                   'HTTP_ACCEPT_LANGUAGE': 'zh,zh-CN;q=0.8,en-US;q=0.6,en;q=0.4',
                   'HTTP_ACCEPT_ENCODING': 'gzip,deflate,sdch'}
    return cgi_environ


class EnvSetup(object):
    "为CGI脚本设置环境变量，以及将标准输出替换成自己的以获取输出"
    def __init__(self, output=True):
        self.output = output

    def __enter__(self):
        self.backup_env = os.environ
        import web
        os.environ  = create_cgi_environ()
        web.cgi_environ = os.environ

        self.io = StringIO.StringIO()
        self.backup_stdout = sys.stdout
        sys.stdout = self.io
        if not PRINT_STDERR:
            sys.stderr = StringIO.StringIO()   # no logging info

        return self

    def __exit__(self, type, value, traceback):
        sys.stdout = self.backup_stdout
        os.environ = self.backup_env
        if self.output:
            print
            print self.getoutput()

    def getoutput(self):
        return self.io.getvalue()

    def __getitem__(self, key):
        return os.environ[key]

    def __setitem__(self, key, value):
        os.environ[key] = value

    def __delitem__(self, key):
        del os.environ[key]


class WriteStdin:
    "替换cgi的输入流"
    def __init__(self, data):
        self._data = data

    def __enter__(self):
        import web
        web.cgi_fp = StringIO.StringIO()
        web.cgi_fp.write(self._data)
        web.cgi_fp.seek(0)

    def __exit__(self, type, value, traceback):
        import web
        web.cgi_fp = sys.stdin


class Test(unittest.TestCase):
    output = True

    def is_in(self, target_string, *args):
        self.assertTrue(is_in(target_string, *args))

    def testHello(self):
        with EnvSetup(self.output):
            main.main()

    def testAccount(self):
        with EnvSetup(self.output) as env:
            env["REQUEST_URI"] = "/accounts"
            main.main()
            self.is_in(env.getoutput(),
                       "Location: /accounts/login",
                       "Status: (2|3)")

    def testUserWhenNotLogin(self):
        "测试未登录时访问用户家目录/user"
        with EnvSetup(self.output) as env:
            env["REQUEST_URI"] = "/user"
            main.main()
            self.is_in(env.getoutput(), "Location: /accounts/login")
            self.is_in(env.getoutput(), "Status: (2|3)")

    def testUserLogin(self):
        "测试登陆"
        # 注册用户a
        with EnvSetup(output=False) as env:
            env["REQUEST_METHOD"] = "POST"
            env["REQUEST_URI"] = "/accounts/new"
            env["Content-Type"] = "application/x-www-form-urlencoded"

            username = "a"
            email = username + "@gmail.com"
            body = "username=%s&email=%s&password=123123&password-again=123123" % (username, email)
            env["Content-Length"] = str(len(body))

            with WriteStdin(body):
                main.main()

        with EnvSetup(self.output) as env:
            env["REQUEST_URI"] = "/accounts/login"
            env["REQUEST_METHOD"] = "POST"
            env["Content-Type"] = "application/x-www-form-urlencoded"

            body = "username=a&password=123123"
            env["Content-Length"] = str(len(body))

            with WriteStdin(body):
                main.main()

            output = env.getoutput()
            self.is_in(output,
                       "Location: ",
                       "Status: (2|3)",
                       "Set-Cookie: session_id=[a-z0-9]")

    def testSignup(self, username=None):
        "测试注册"
        with EnvSetup(self.output) as env:
            env["REQUEST_METHOD"] = "POST"
            env["REQUEST_URI"] = "/accounts/new"
            env["Content-Type"] = "application/x-www-form-urlencoded"

            username = "".join(random.choice(string.lowercase + string.digits) for i in xrange(16))
            email = username + "@gmail.com"
            body = "username=%s&email=%s&password=asdf&password-again=asdf" % (username, email)
            env["Content-Length"] = str(len(body))

            with WriteStdin(body):
                main.main()

            output = env.getoutput()
            self.is_in(output,
                       "Location: ",
                       "Status: 3")

    def testSignupWithNonValidUsername(self):
        "不合法用户名注册测试"

        non_valid_username = ("rose!", "Steve John",
                              "a+1", ".ss", "hua.liang"
                              )
        for username in non_valid_username:
            # 非法用户名
            with EnvSetup(self.output) as env:
                env["REQUEST_METHOD"] = "POST"
                env["REQUEST_URI"] = "/accounts/new"
                env["Content-Type"] = "application/x-www-form-urlencoded"

                email = "rose@gmail.com"
                body = "username=%s&email=%s&password=asdf&password-again=asdf" % (username, email)
                env["Content-Length"] = str(len(body))

                with WriteStdin(body):
                    main.main()

                output = env.getoutput()
                self.is_in(output,
                           "not valid",
                           "Status: [^23]")

    def testSignupWithNonValidEmail(self):
        "不合法邮箱注册测试"

        non_valid_email = ("a", "a@asdf..com", "xx@aaa", "helo!@dfdfa.com",
                           "http://EverET.org", "1 + 1", "asdf+qwe@a.com",
                           "hello@.com", "sdfsdf.com.cn")
        for email in non_valid_email:
            # 非法用户名
            with EnvSetup(self.output) as env:
                env["REQUEST_METHOD"] = "POST"
                env["REQUEST_URI"] = "/accounts/new"
                env["Content-Type"] = "application/x-www-form-urlencoded"

                username = "Jack"
                body = "username=%s&email=%s&password=asdf&password-again=asdf" % (username, email)
                env["Content-Length"] = str(len(body))

                with WriteStdin(body):
                    main.main()

                output = env.getoutput()
                self.is_in(output, "not valid")
                self.is_in(output, "Status: [^23]")


if __name__ == '__main__':
    unittest.main()
