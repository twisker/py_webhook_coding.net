#!/usr/bin/env python
import hmac
import hashlib
from wsgiref.simple_server import make_server
import os

__CODING_SECRET_TOKEN__ = "generate_your_secret_token"
__CODING_SIGNATURE__HEAD__ = "HTTP_X_CODING_SIGNATURE"
__CODING_EVENT_HEAD__ = "HTTP_X_CODING_EVENT"


def verify_token(body, signature):
    s = "sha1=%s" % hmac.new(__CODING_SECRET_TOKEN__.encode("utf-8"), body, digestmod=hashlib.sha1).hexdigest()
    return s == signature


def application(environ, start_response):
    response_body = "Invalid Request"
    status = "403 Forbidden"
    if environ.get("REQUEST_METHOD", "GET") == "POST":
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        request_body = environ['wsgi.input'].read(request_body_size)
        if verify_token(request_body, environ.get(__CODING_SIGNATURE__HEAD__, None)):
            # 处理不同事件
            event = environ.get(__CODING_EVENT_HEAD__, "ping")
            if event == "push":
                os.chdir("/path/to/your/local/repos")
                os.system("git pull origin master")
                response_body = "repos pulled"
                status = '200 OK'
            elif event == "ping":
                status = '200 OK'
                response_body = "ping succeed"
    start_response(status, [('Content-Type', 'text/plain')])
    return [response_body.encode("utf-8")]


if __name__ == "__main__":
    # for test purpose only
    httpd = make_server('0.0.0.0', 17838, application)
    httpd.serve_forever()
