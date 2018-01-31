#! /usr/bin/env python
# -*- coding:utf-8 -*-

from functools import wraps
import shutil
import urllib2
import cookielib
import requests
import lxml.html
from urldl import URLDownload


class NURLDownload(URLDownload):
    def __init__(self):
        super(NURLDownload, self).__init__()
        self.cjar = cookielib.CookieJar()
        self.opener =\
            urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cjar))

    def _decorator(explain):
        def _deco(function):
            @wraps(function)
            def __deco(*args, **kw):
                special = ['generator', 'list']
                if any(spc in function.__name__ for spc in special):
                    print explain, '\n',
                else:
                    print '==>', explain, '\n\t',
                function(*args, **kw)
            return __deco
        return _deco

    @_decorator('Downloading')
    def download(self, url):
        print url
        res = requests.get(url, stream=True)
        filename_list = url.split('/')
        filename =\
            '_'.join(filename_list[len(filename_list)-7:len(filename_list)])
        filepath = self._savepath + filename
        with open(filepath, 'wb') as fobj:
            shutil.copyfileobj(res.raw, fobj)

    @_decorator('Downloading')
    def dcimg_download(self, parent_url):
        target_html = requests.get(parent_url).content
        root = lxml.html.fromstring(target_html)
        target_data = root.cssselect('img')[0]
        target_url = target_data.attrib['src']

        print target_url
        value = target_url.split('/')[-1].split('=')[-1]
        filepath = self._savepath + value + '.jpg'

        self.opener.open(parent_url)
        req = urllib2.Request(target_url)

        with open(filepath, 'wb') as savefile:
            savefile.write(self.opener.open(req).read())
