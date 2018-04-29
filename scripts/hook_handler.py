#!/usr/bin/env python
import hmac
import hashlib
from wsgiref.simple_server import make_server
import json
import os

__SECRET_TOKEN__ = "generate_your_secret_token"
__SIGNATURE__HEAD__ = "HTTP_X_CODING_SIGNATURE"

def verify_token(body, signature):
    s = "sha1=%s" % hmac.new(__SECRET_TOKEN__.encode("utf-8"), body, digestmod=hashlib.sha1).hexdigest()
    return s == signature


def application(environ, start_response):
    # POST or GET ?
    method = environ['REQUEST_METHOD']
    response_body = "OK"
    status = '200 OK'

    if method == "POST":
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        request_body = environ['wsgi.input'].read(request_body_size)
        if __SIGNATURE__HEAD__ in environ and verify_token(request_body, environ[__SIGNATURE__HEAD__]):
            data = json.loads(request_body.decode("utf-8"))
            # 如果是push事件
            if "hook" in data and "events" in data["hook"] and "push" in data["hook"]["events"]:
                os.chdir("/path/to/your/local/repos")
                os.system("git pull origin master")
                response_body = "repos pulled"
        else:
            response_body = "Invalid Request"
            status = "403 Forbidden"
    response_headers = [
        ('Content-Type', 'text/html'),
    ]

    start_response(status, response_headers)
    return [response_body.encode("utf-8")]


if __name__ == "__main__":
    # for test purpose only
    httpd = make_server('0.0.0.0', 17838, application)
    httpd.serve_forever()