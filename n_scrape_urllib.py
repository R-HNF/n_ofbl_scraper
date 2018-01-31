#! /usr/bin/env python
# -*- coding:utf-8 -*-

from functools import wraps
import sys
import time
import urllib2
import lxml.html


_DOMAIN_URL = 'http://hoge.n.com'
TIME_SLEEP = 0.8


class NScrape(object):
    def __init__(self):
        self.latest_image_url = ''
        self.new_latest_image_url = ''
        self.image_number = 0
        self.error_list = []
        self.dler = None
        sys.setrecursionlimit(100000)  # recursion limit

    def _decorator(explain):
        def _deco(function):
            @wraps(function)
            def __deco(*args, **kw):
                print '==>', explain, '\n\t',
                function(*args, **kw)
                print '-' * 46
            return __deco
        return _deco

    @_decorator('Latest image URL')
    def set_latest_image_url(self, url):
        self.latest_image_url = url
        self.new_latest_image_url = url
        print self.latest_image_url

    def set_dler(self, dler):
        self.dler = dler

    def get_new_latest_image_url(self):
        return self.new_latest_image_url

    def get_image_urls(self, img_tags):
        last = False
        image_urls = []

        for img_tag in img_tags:
            parent_tag = img_tag.getparent()

            if parent_tag is not None:
                if (parent_tag.tag == 'a') and\
                        ('href' in parent_tag.attrib) and\
                        ('dcimg' in parent_tag.attrib['href']) and\
                        (parent_tag.attrib['href'] not in image_urls):
                    if parent_tag.attrib['href'] == self.latest_image_url:
                        last = True
                        break
                    if parent_tag.attrib['href'] not in image_urls:
                        image_urls.append(parent_tag.attrib['href'])
                elif 'src' in img_tag.attrib:
                    _conditions = [
                        ('gif' not in img_tag.attrib['src']),
                        ('n46_list' not in img_tag.attrib['src'])
                    ]
                    __conditions = [
                        ('.jpeg' in img_tag.attrib['src'].lower()),
                        ('.jpg' in img_tag.attrib['src'].lower()),
                        ('.png' in img_tag.attrib['src'].lower())
                    ]
                    if all(_ for _ in _conditions) and\
                            any(_ for _ in __conditions):
                        if img_tag.attrib['src'] == self.latest_image_url:
                            last = True
                            break
                        if img_tag.attrib['src'] not in image_urls:
                            image_urls.append(img_tag.attrib['src'])

        image_urls.reverse()
        return last, image_urls

    def get_next_page(self, a_tags):
        next_page = ''
        next_month = ''
        for a_tag in a_tags:
            if a_tag.text == u'＞':
                next_page = _DOMAIN_URL + '/' + a_tag.attrib['href']
                return next_page
            if 'class' in a_tag.attrib:
                if a_tag.attrib['class'] == 'prev':
                    next_month = a_tag.attrib['href']

        if next_month != '':
            next_page = next_month
            return next_page

    @_decorator('Target page')
    def scrape(self, target_page):
        print target_page
        hdr={'User-Agent': 'Mozilla/5.0'}
        req = urllib2.Request(target_page, headers=hdr)
        responses = urllib2.urlopen(req)
        target_html = responses.read()
        root = lxml.html.fromstring(target_html)
        img_tags = root.cssselect('img')
        a_tags = root.cssselect('a')

        last, image_urls = self.get_image_urls(img_tags)

        if last is False:
            next_page = self.get_next_page(a_tags)
            self.scrape(next_page)
        else:
            print 'Found latst image URL', '-' * 24, '\n'

        print target_page
        for image_url in image_urls:
            try:
                if 'dcimg' in image_url:
                    self.dler.dcimg_download(image_url)
                else:
                    self.dler.download(image_url)
                self.image_number += 1
            except:
                self.error_list.append(image_url)
            time.sleep(TIME_SLEEP)

        if len(image_urls) > 0:
            self.new_latest_image_url = image_urls[-1]
