# Decompiled from http_cmd.pyc (Python 3.8)
from urllib import request
from urllib import error


def getHTMLText(url):
    req = request.Request(url)
    try:
        response = request.urlopen(req)
        html = response.read().decode('utf-8')
        print('网页文件打开正常，%s' % response.code)
        return html
    except error.URLError as e:
        print('网页打开异常，%s' % e.reason)
        return 'Error'
