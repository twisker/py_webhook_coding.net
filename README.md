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

    apt-get install supervisord
    
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
response_body = "OK"
status = '200 OK'
```
    
