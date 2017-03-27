# -*-coding:utf-8-*-
__author__ = 'lpp'

import threading
import Queue
from bs4 import BeautifulSoup
import re
import requests
import time


def getCookieDic(cookie_path):
    f = open(cookie_path, 'r')
    raw_cookie = f.readline().strip()
    f.close()
    cookies = {}
    for line in raw_cookie.split(';'):
        key, value = line.split('=', 1)
        cookies[key] = value
    return cookies


class UrlThread(threading.Thread):
    def __init__(self, queue, out_queue, cookieDic):
        threading.Thread.__init__(self)
        self.queue = queue
        self.out_queue = out_queue
        self.cookie_dict = cookieDic

    def run(self):
        while not exitFlag:
            curr_path = self.queue.get()
            temp_id = curr_path.split(url_base)[1].split('/')[0]
            try:
                resp = requests.get(curr_path, cookies=self.cookie_dict)
                chunk = resp.text
                self.out_queue.put([curr_path, temp_id, chunk])
                self.queue.task_done()
            except Exception as e:
                print("grab error with request " + curr_path)
                print(e)
                continue


class SoupingThread(threading.Thread):
    def __init__(self, queue, out_queue, done, dic):
        threading.Thread.__init__(self)
        self.queue = queue
        self.out_queue = out_queue
        self.done = done
        self.count_dic = dic

    def run(self):
        while not exitFlag:
            curr_path, temp_id, chunk = self.out_queue.get()[:]

            try:
                # begin souping
                soup = BeautifulSoup(chunk, 'html.parser')
                count = 3
                while not soup and count > 0:
                    soup = BeautifulSoup(chunk, 'html.parser')
                    count -= 1

                if not soup:
                    pass  # soup none
                else:
                    if 'status' not in curr_path:
                        # homepage
                        for i in soup.find_all(href=re.compile("statuses")):
                            tempUrl = i["href"]
                            if re.match('http', tempUrl) and tempUrl not in self.done:
                                # add statuses page into queue
                                self.queue.put(tempUrl)
                                self.done.add(tempUrl)
                    else:
                        # status page
                        status_list = soup.find_all(class_=re.compile("new-status"))
                        if len(status_list) > 0:
                            # do sth with the status ...
                            if temp_id not in self.count_dic:
                                self.count_dic[temp_id] = len(status_list)
                            else:
                                self.count_dic[temp_id] += len(status_list)

                            # add other status page into queue
                            for i in soup.find_all(href=re.compile("\?p=")):
                                if i["href"] == '?p=1':
                                    pass
                                else:
                                    tempUrl = curr_path.split("statuses")[0] + 'statuses' + i["href"]
                                    if tempUrl not in self.done:
                                        self.queue.put(tempUrl)
                                        self.done.add(tempUrl)
                        else:
                            # no status in this page
                            pass
                self.out_queue.task_done()
            except Exception as e:
                print('error with souping ' + curr_path)
                print(e)
                continue


if __name__ == '__main__':
    url_base = "https://www.douban.com/people/"
    cookiePath = 'cookieStr.txt'  # cookie string
    cookie_dict = getCookieDic(cookiePath)  # convert cookie string to dict
    id_list = ['4865787', '32325066']
    req_queue = Queue.Queue()
    soup_queue = Queue.Queue()
    done = set()
    count_dic = {}  # status number for each person

    exitFlag = False

    for i in range(5):
        req_t = UrlThread(req_queue, soup_queue, cookie_dict)
        # req_t.setDaemon(True)
        req_t.start()

    for name in id_list:
        req_queue.put(url_base + name + '/')
        done.add(url_base + name + '/')

    for i in range(10):
        soup_t = SoupingThread(req_queue, soup_queue, done, count_dic)
        # soup_t.setDaemon(True)
        soup_t.start()

    req_queue.join()
    soup_queue.join()

    print count_dic
    exitFlag = True
    print 'main thread exit'
