# -*-coding:utf-8-*-
__author__ = 'lpp'

import Queue
# import urllib2
from bs4 import BeautifulSoup
import re
import cookielib
import requests


def getCookieDic(cookie_path):
    f = open(cookie_path, 'r')
    raw_cookie = f.readline().strip()
    f.close()
    cookies = {}
    for line in raw_cookie.split(';'):
        key, value = line.split('=', 1)
        cookies[key] = value
    return cookies


url_base = "https://www.douban.com/people/"
id_list = ['159488666']
work_queue = Queue.Queue()
done = set()
cookiePath = 'cookie.txt'
cookie_dict = getCookieDic(cookiePath)

for name in id_list:
    work_queue.put(url_base + name + '/')
    done.add(url_base + name + '/')

while not work_queue.empty():
    curr_path = work_queue.get()
    try:
        resp = requests.get(curr_path, cookies=cookie_dict)
        chunk = resp.text
        # print chunk

        # begin souping
        soup = BeautifulSoup(chunk, 'html.parser')
        count = 3
        while not soup and count > 0:
            soup = BeautifulSoup(chunk, 'html.parser')
            count -= 1

        if not soup:
            print("soup null ...")
        else:
            # print soup
            if 'status' not in curr_path:
                print("index page")
                for i in soup.find_all(href=re.compile("statuses")):
                    tempUrl = i["href"]
                    if re.match('http', tempUrl) and tempUrl not in done:
                        print tempUrl, 'added'
                        work_queue.put(tempUrl)
                        done.add(tempUrl)
            else:
                print("other page")
                if len(soup.find_all(class_=re.compile("new-status"))) > 0:
                    for i in soup.find_all(href=re.compile("\?p=")):
                        if i["href"] == '?p=1':
                            pass
                        else:
                            tempUrl = curr_path.split("statuses")[0] + 'statuses' + i["href"]
                            if tempUrl not in done:
                                print tempUrl, 'added'
                                work_queue.put(tempUrl)
                                done.add(tempUrl)
                else:
                    pass
    except Exception as e:
        print("grab error in " + curr_path)
        continue
