# py_webhook_coding.net
a very very simple webhook written in python for coding.net repos events

## 目的
有几个基于Django的项目，需要自动部署。代码库在Coding.net上。Coding.Net本身提供了Webhook机制。所以需要在服务器上部署webhook handler。
目前网上找到的webhook handler都太重，我需要一个轻量级的，可快速部署在阿里云linux主机上的webhook handler方案。

## 技术要点

1. 需要起进程。方案：用supervisor
2. 需要起HTTP服务。方案：用uwsgi
3. 需要处理POST请求，并在其中处理各种event。方案：用python写wsgi脚本
4. 需要处理基于HASH签名的校验机制。方案：python

## 详细步骤

### 1、安装supervisor

可以在ubuntu命令行，使用如下命令：

    apt-get install supervisor
    
### 2、安装uwsgi

使用如下命令，安装python / virtualenv，创建一个虚拟环境，并激活：

    apt-get install build-essential python-dev virtualenv
    virtualenv .venv
    source .venv/bin/activate
    
然后使用pip安装uwsgi

    pip install uwsgi

### 3、写python脚本

使用以下类似的python脚本。

```python
#!/usr/bin/python
import os

def application(environ, start_response):
    os.chdir("/path/to/your/local/repos")       # 进入你的git目录
    os.system("git pull origin master")         # 运行git命令，进行更新
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [b'OK']

```

如果要处理令牌加密，可使用类似以下的代码：

```python
#!/usr/bin/python
import hmac
import hashlib
import os

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
            os.chdir("/path/to/your/local/repos")
            os.system("git pull origin master")
            response_body = "repos pulled"
            status = '200 OK'
    start_response(status, [('Content-Type', 'text/plain')])
    return [response_body.encode("utf-8")]

```

更详细的代码请参见 scripts/hook_handler.py

### 4、创建uwsgi.ini

在合适的目录，比如，与楼上python代码同一目录，创建uwsgi的运行参数文件，uwsgi.ini，内容如下：

    [uwsgi]
    http    = :17838
    chdir   = /home/for/your/scripts
    venv    = /home/for/virtualenv
    wsgi-file   = hook_handler.py
    processes = 4
    threads = 2
    master = true

可以使用如下命令对此文件进行测试：

    uwsgi uwsgi.ini

也可参见 scripts/hook_uwsgi.ini

### 5、创建supervisor的配置文件

到/etc/supervisor/conf.d/目录下，为楼上的uwsgi创建配置文件，hook.conf，内容如下：

    [program:web_hook_coding_net]
    autostart = true
    user=your_user
    command=/path/to/your/virtualenv/bin/uwsgi /path/to/your/hook_uwsgi.ini
    priority=1
    redirect_stderr=true
    stopsignal=INT

也可参见 scripts/hook_supervisor.conf

创建成功后，重启supervisor

    systemctl restart supervisor

至此，你的coding.net上的项目如果有push提交，这边的repos已经可以自动更新了。

*注意，如果是py文件，需要配合uwsgi的--touch-reload参数，或gunicorn的--reload参数共同使用，才能实现代码级的reload。*
