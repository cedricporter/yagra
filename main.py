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
import Cookie
import sys


class StdStream(object):
    """Standard output stream"""

    def write(self, str):
        sys.stdout.write(str)


class HTTPConnection(object):
    def __init__(self, stream):
        self.stream = stream

    def close(self):
        self.stream.close()

    def write(self, chunk):
        self.stream.write(chunk)


class HTTPRequest(object):
    def __init__(self, method, uri, query, headers=None,
                 remote_ip=None, host=None, connection=None
                 ):
        self.method = method
        self.uri = uri
        self.headers = headers
        self.host = host or self.headers.get("Host")
        self.remote_ip = remote_ip
        self.query = query
        self.arguments = {}
        self.connection = connection

        arguments = urlparse.parse_qs(self.query)
        for name, values in arguments.iteritems():
            values = [v for v in values if v]
            if values:
                self.arguments[name] = values

    def write(self, chunk):
        self.connection.write(chunk)


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

        self.clear()

    def get(self, *args, **kwargs):
        raise HTTPError(405)

    def post(self, *args, **kwargs):
        raise HTTPError(405)

    def clear(self):
        self._headers = {
            "Content-Type": "text/html; charset=UTF-8",
        }
        self._list_headers = []
        self._write_buffer = []
        self._status_code = 200

    def set_status(self, status_code):
        assert status_code in httplib.responses
        self._status_code = status_code

    def set_header(self, name, value):
        self._headers[name] = self._convert_to_header_value(value)

    def add_header(self, name, value):
        self._list_headers.append((name,
                                   self._convert_to_header_value(value)))

    def clear_header(self, name):
        if name in self._headers:
            del self._headers[name]

    def _convert_to_header_value(self, value):
        if isinstance(value, str):
            pass
        elif isinstance(value, unicode):
            value = value.encode("utf-8")
        elif isinstance(value, (int, long)):
            return str(value)
        else:
            raise TypeError("Unsupported value: %r" % value)
        return value

    _ARG_DEFAULT = []

    def get_argument(self, name, default=_ARG_DEFAULT):
        args = self.get_arguments(name)
        if not args:
            if default is self._ARG_DEFAULT:
                raise HTTPError(400)
            return default
        return args[-1]

    def get_arguments(self, name):
        values = []
        for v in self.request.arguments.get(name, []):
            values.append(v)    # might need decode to unicode
        return values

    @property
    def cookies(self):
        return self.request.cookies

    def set_cookie(self, name, value):
        if not hasattr(self, "_new_cookie"):
            self._new_cookie = Cookie.SimpleCookie()
        self._new_cookie[name] = value

    def write(self, chunk):
        self._write_buffer.append(chunk)

    def flush(self):
        self.request.write("Status: %d %s" % (self._status_code,
                                              httplib.responses[self._status_code]))
        for k, v in self._headers.iteritems():
            self.request.write("%s: %s\r\n" % (k, v))
        self.request.write("\r\n")
        self.request.write("".join(self._write_buffer))

    def _execute(self):
        self.write("Hello, ET")

        self.flush()


class Application(object):
    def __init__(self):
        pass

    def prepare(self):
        connection = HTTPConnection(StdStream())

        env = os.environ
        request = HTTPRequest(env["REQUEST_METHOD"],
                              env["REQUEST_URI"],
                              env.get("QUERY_STRING"),
                              None,
                              env["REMOTE_ADDR"],
                              env.get("HTTP_HOST"),
                              connection)
        self._request = request

        self.handler = RequestHandler(self, self._request)

    def handle(self):
        self.handler._execute()

    def run(self):
        self.prepare()

        self.handle()


if __name__ == '__main__':
    app = Application()
    app.run()
