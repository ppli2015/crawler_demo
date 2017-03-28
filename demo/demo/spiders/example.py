# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request, FormRequest
from demo.demo.items import StatusItem




class DoubanStatusSpider(scrapy.Spider):
    name = "douban"
    allowed_domains = ["douban.com"]
    start_urls = ['https://www.douban.com/people/159488666/']

    def parse(self, response):
        print response

        item = StatusItem()
        item['user_name'] = response.url.split("/")[4]
        item['timestamp'] = ''
        item['content'] = ''
        yield item

    def start_requests(self):
        return [Request("https://www.douban.com/login", callback=self.post_login)]

    def post_login(self, response):
        print "preparing login ==="
        return [FormRequest.from_response(response,
                                          meta={'cookiejar': response.meta['cookiejar']},
                                          headers=self.headers,  # 注意此处的headers
                                          formdata={
                                              'email': '1095511864@qq.com',
                                              'password': '123456'
                                          },
                                          callback=self.after_login,
                                          dont_filter=True
                                          )]

    def after_login(self):
        for url in self.start_urls:
            yield self.make_requests_from_url(url)
