#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#

import unittest
import main
import StringIO
import sys
import os


def create_cgi_environ():
    cgi_environ = {'HTTP_COOKIE': '',
                   'REQUEST_URI': '/imagewall?name=cedricporter&age=22',
                   'SERVER_SOFTWARE': 'Apache/2.2.22 (Ubuntu)',
                   'SCRIPT_NAME': '/main.py',
                   'REQUEST_METHOD': 'GET',
                   'SERVER_PROTOCOL': 'HTTP/1.1',
                   'QUERY_STRING': 'name=cedricporter&age=22',
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
    def __init__(self, output=True):
        self.output = output

    def __enter__(self):
        self.backup_env = os.environ
        os.environ  = create_cgi_environ()

        self.io = StringIO.StringIO()
        self.backup_stdout = sys.stdout
        sys.stdout = self.io
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


class Test(unittest.TestCase):
    output = True

    def testHello(self):
        with EnvSetup(self.output):
            main.main()

    def testAccount(self):
        with EnvSetup(self.output) as env:
            env["REQUEST_URI"] = "/accounts"
            main.main()
            self.assertTrue("Location: /accounts/login" in env.getoutput())

    def testUserWhenNotLogin(self):
        with EnvSetup(self.output) as env:
            env["REQUEST_URI"] = "/user"
            main.main()
            self.assertTrue("Location: /accounts/login" in env.getoutput())

    def testUserLogin(self):
        with EnvSetup(self.output) as env:
            env["REQUEST_URI"] = "/accounts/login"
            env["REQUEST_METHOD"] = "POST"

            body = "username=a&password=123123"


if __name__ == '__main__':
    unittest.main()
