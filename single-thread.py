# -*-coding:utf-8-*-
__author__ = 'lpp'

import Queue
from bs4 import BeautifulSoup
import re
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


if __name__ == '__main__':
    url_base = "https://www.douban.com/people/"
    id_list = ['4865787', 'hana.magic', '32325066']
    work_queue = Queue.Queue()
    done = set()
    cookiePath = 'cookie.txt'  # cookie string
    cookie_dict = getCookieDic(cookiePath)  # convert cookie string to dict
    count_dic = {}  # status number for each person

    for name in id_list:
        work_queue.put(url_base + name + '/')
        done.add(url_base + name + '/')

    while not work_queue.empty():
        curr_path = work_queue.get()
        temp_id = curr_path.split(url_base)[1].split('/')[0]

        try:
            resp = requests.get(curr_path, cookies=cookie_dict)
            chunk = resp.text

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
                        if re.match('http', tempUrl) and tempUrl not in done:
                            # add statuses page into queue
                            work_queue.put(tempUrl)
                            done.add(tempUrl)
                else:
                    # status page
                    status_list = soup.find_all(class_=re.compile("new-status"))
                    if len(status_list) > 0:
                        # do sth with the status ...
                        if temp_id not in count_dic:
                            count_dic[temp_id] = len(status_list)
                        else:
                            count_dic[temp_id] += len(status_list)

                        # add other status page into queue
                        for i in soup.find_all(href=re.compile("\?p=")):
                            if i["href"] == '?p=1':
                                pass
                            else:
                                tempUrl = curr_path.split("statuses")[0] + 'statuses' + i["href"]
                                if tempUrl not in done:
                                    work_queue.put(tempUrl)
                                    done.add(tempUrl)
                    else:
                        # no status in this page
                        pass
        except Exception as e:
            print("grab error at " + curr_path)
            print(e)
            continue

    print(count_dic)
