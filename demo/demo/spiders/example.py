# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request,FormRequest


class DoubanStatusSpider(scrapy.Spider):
    name = "douban"
    allowed_domains = ["douban.com"]
    start_urls = ['https://www.douban.com/people/159488666/']

    def parse(self, response):
        print response

    def start_requests(self):
        return [Request("https://www.douban.com/login",callback=self.post_login)]

    def post_login(self,response):
        print "preparing login ==="
        return [FormRequest()]