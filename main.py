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
    <form action="/user" method="post">
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
        self.write(self.get_argument("username"))

        user_head = self.get_argument("user_head")

        with open("uploads/user_head.jpg", "wb") as out:
            out.write(user_head)


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
