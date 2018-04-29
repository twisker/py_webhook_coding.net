#!/usr/bin/env python

from wsgiref.simple_server import make_server
import json
import os


def application(environ, start_response):
    # POST or GET ?
    method = environ['REQUEST_METHOD']
    response_body = "OK"
    status = '200 OK'

    if method == "POST":
        # the environment variable CONTENT_LENGTH may be empty or missing
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0

        # When the method is POST the variable will be sent
        # in the HTTP request body which is passed by the WSGI server
        # in the file like wsgi.input environment variable.
        request_body = environ['wsgi.input'].read(request_body_size)
        data = json.loads(request_body.decode("utf-8"))
        print(data)
    elif method == "GET":
        response_body = "OK"

    response_headers = [
        ('Content-Type', 'text/html'),
    ]

    start_response(status, response_headers)
    return [response_body.encode("utf-8")]


if __name__ == "__main__":
    # for test purpose only
    httpd = make_server('0.0.0.0', 17838, application)
    httpd.serve_forever()