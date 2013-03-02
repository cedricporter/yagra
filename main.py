#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#

import cgitb
cgitb.enable()

import cgi
import os
import pprint
import urlparse
import httplib


class HTTPRequest(object):
    def __init__(self, method, uri, query, headers=None,
                 remote_ip=None, host=None
                 ):
        self.method = method
        self.uri = uri
        self.headers = headers
        self.host = host or self.headers.get("Host")
        self.remote_ip = remote_ip
        self.query = query
        self.arguments = {}

        arguments = urlparse.parse_qs(self.query)
        for name, values in arguments.iteritems():
            values = [v for v in values if v]
            if values:
                self.arguments[name] = values

    def get_argument(self, key):
        return self.arguments.get(key, None)


class HTTPError(Exception):
    """An exception that will turn into an HTTP error response."""
    def __init__(self, status_code, log_message=None, *args):
        self.status_code = status_code
        self.log_message = log_message
        self.args = args

    def __str__(self):
        message = "HTTP %d: %s" % (
            self.status_code, httplib.responses[self.status_code])
        if self.log_message:
            return message + " (" + (self.log_message % self.args) + ")"
        else:
            return message


class RequestHandler(object):
    """Subclass this class"""

    def __init__(self, application, request, **kwargs):
        super(RequestHandler, self).__init__()

        self.application = application
        self.request = request

    def get(self, *args, **kwargs):
        raise HTTPError(405)

    def post(self, *args, **kwargs):
        raise HTTPError(405)


class Application(object):
    def __init__(self):
        self.ctx = {}
        self._write_buffer = []
        self.headers = []

    def write(self, data):
        self._write_buffer.append(data)

    def parse(self):
        env = os.environ
        request = HTTPRequest(env["REQUEST_METHOD"],
                              env["REQUEST_URI"],
                              env.get("QUERY_STRING"),
                              None,
                              env["REMOTE_ADDR"],
                              env.get("HTTP_HOST"))
        self._request = request

    def run(self):
        # header
        self.header("Content-type", "text/html")

        # parse
        self.parse()

        # output
        self.write("Hello")
        self.write(", ET")
        self.write(pprint.pformat(self._request.__dict__))
        self.send_all()

    def header(self, key, value):
        self.headers.append((key, value))

    def send_all(self):
        for header in self.headers:
            print "%s: %s" % header
        print
        print "".join(self._write_buffer)


if __name__ == '__main__':
    app = Application()
    app.run()
