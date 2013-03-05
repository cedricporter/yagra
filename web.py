#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#

import Cookie
import calendar
import cgi
import datetime
import email
import httplib
import os
import re
import sys
import traceback
import urlparse

from util import import_object


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
        self.path = uri.split("?", 1)[0]
        self.headers = headers
        self.host = host or self.headers.get("Host")
        self.remote_ip = remote_ip
        self.query = query
        self.arguments = {}
        self.connection = connection
        self.files = {}

        # TODO: 这里需要将cgi底层操作独立抽象出来
        form = cgi.FieldStorage()
        for key in form.keys():
            item = form[key]
            if item.file:
                self.files[key] = item

            self.arguments[key] = form.getlist(key)

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

        self.initialize(**kwargs)

    def initialize(self):
        pass

    def prepare(self):
        pass

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

    def set_cookie(self, name, value, domain=None, expires=None, path="/",
                   expires_days=None, max_age=None):

        if not hasattr(self, "_new_cookie"):
            self._new_cookie = Cookie.SimpleCookie()
        self._new_cookie[name] = value
        morsel = self._new_cookie[name]
        if domain:
            morsel["domain"] = domain
        if expires_days is not None and not expires:
            expires = datetime.datetime.utcnow() + datetime.timedelta(
                days=expires_days)
        if expires:
            timestamp = calendar.timegm(expires.utctimetuple())
            morsel["expires"] = email.utils.formatdate(
                timestamp, localtime=False, usegmt=True)
        if path:
            morsel["path"] = path
        if max_age:
            morsel["max_age"] = max_age

    def clear_cookie(self, name, path="/", domain=None):
        expires = datetime.datetime.utcnow() - datetime.timedelta(days=365)
        self.set_cookie(name, value="", path=path,
                        expires=expires, domain=domain)

    def redirect(self, url, permanent=False, status=None):
        if status is None:
            status = 301 if permanent else 302
        self.set_status(status)
        self.set_header("Location", urlparse.urljoin(self.request.uri,
                                                     url))

    def write(self, chunk):
        self._write_buffer.append(chunk)

    def _generate_headers(self):
        lines = ["Status: %d %s" % (self._status_code,
                                        httplib.responses[self._status_code])]

        for k, v in self._headers.iteritems():
            lines.append("%s: %s" % (k, v))
        if hasattr(self, "_new_cookie"):
            for cookie in self._new_cookie.values():
                lines.append("Set-Cookie: " + cookie.OutputString(None))

        return "\r\n".join(lines) + "\r\n\r\n"

    def flush(self):
        header = self._generate_headers()
        self.request.write(header)

        self.request.write("".join(self._write_buffer))

    def _execute(self):
        try:
            self.prepare()

            getattr(self, self.request.method.lower())()
        except Exception, e:
            self._handle_request_exception(e)
        finally:
            self.flush()

    def _handle_request_exception(self, e):
        if isinstance(e, HTTPError):
            self.send_error(e.status_code, exc_info=traceback.format_exc())
        else:
            self.send_error(500, exc_info=traceback.format_exc())

    def send_error(self, status_code=500, **kwargs):
        self.clear()
        self.set_status(status_code)
        self.set_header("Content-Type", "text/plain")

        self.write(kwargs.get("exc_info", ""))


class ErrorHandler(RequestHandler):
    def initialize(self, status_code):
        self.set_status(status_code)

    def prepare(self):
        raise HTTPError(self._status_code)


class URLSpec(object):
    def __init__(self, pattern, handler_class):
        if not pattern.endswith("$"):
            pattern += "$"
        self.regex = re.compile(pattern)
        self.handler_class = handler_class


class Application(object):
    """Application is the abstract of the program"""
    def __init__(self, handlers):
        self.handlers = []

        if handlers:
            self.add_handlers(handlers)

    def add_handlers(self, handlers):
        for spec in handlers:
            if isinstance(spec, type(())):
                assert len(spec) == 2
                host_pattern = spec[0]
                handler = spec[1]

                if isinstance(handler, str):
                    handler = import_object(handler)

                if not host_pattern.endswith("$"):
                    host_pattern += "$"

                self.handlers.append(URLSpec(host_pattern, handler))

    def prepare(self, stream):
        connection = HTTPConnection(stream)

        env = os.environ
        request = HTTPRequest(env["REQUEST_METHOD"],
                              env["REQUEST_URI"],
                              env.get("QUERY_STRING"),
                              None,
                              env["REMOTE_ADDR"],
                              env.get("HTTP_HOST"),
                              connection)
        self._request = request

    def handle(self):
        request = self._request
        path = request.path

        handler = None

        for spec in self.handlers:
            match = spec.regex.match(path)
            if match:
                handler = spec.handler_class(self, request)

        if not handler:
            handler = ErrorHandler(self, request, status_code=404)

        handler._execute()
        return handler

    def cgi_run(self):
        self.prepare(StdStream())

        self.handle()
