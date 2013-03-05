#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#

import cgitb
cgitb.enable()

import web


class MainHandler(web.RequestHandler):
    def get(self):
        html = """
<html>
  <head>
    <title>
      Yagra
    </title>
  </head>
  <body>
    <form action="/user" method="post" enctype="multipart/form-data">
      <input type="text" name="username"/>
      <input type="file" name="user_head"/>
      <input type="submit"/>
    </form>
  </body>
</html>
        """
        self.write(html)


class UserHandler(web.RequestHandler):
    def post(self):
        user_head = self.get_argument("user_head")

        import random
        import string
        import time

        upload_filename = self.request.files["user_head"].filename

        filename = "uploads/" + time.strftime("%Y_%m_%d_%H_%M_%S_") + "".join(random.choice(string.letters) for i in xrange(10)) + upload_filename

        with open(filename, "wb") as out:
            out.write(user_head)

        self.set_header("Content-Type", "text/plain")
        self.write(str(self.request.files["user_head"].type))

        self.redirect("/")


class EchoHandler(web.RequestHandler):
    def get(self):
        import cgi
        self.write(str(cgi.FieldStorage()))
        self.set_cookie("Name", "Stupid ET")


class EnvironHandler(web.RequestHandler):
    def get(self):
        import os
        self.set_header("Content-Type", "text/plain")
        self.write(str(os.environ))


def main():
    app = web.Application([
        (r"/", MainHandler),
        (r"/echo", EchoHandler),
        (r"/user", UserHandler),
        (r"/env", EnvironHandler),
    ])
    app.cgi_run()


if __name__ == '__main__':
    main()
