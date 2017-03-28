# -*- coding: utf-8 -*-
import scrapy


class DoubanStatusSpider(scrapy.Spider):
    name = "douban"
    allowed_domains = ["douban.com"]
    start_urls = ['https://www.douban.com/people/159488666/']

    def parse(self, response):
        print response
