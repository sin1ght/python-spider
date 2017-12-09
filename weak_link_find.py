'''
网站失效连接检测
'''

import requests
from collections import deque
from pyquery import PyQuery as pq
import re
import threading
import time
import random

url_queue=deque()
visited_queue=deque()

headers={
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0) Gecko/20100101 Firefox/57.0'
}

main_url = 'http://www.sohu.com'
host = 'www.sohu.com'
count=0
proxys=[]


class MainManager:
    def __init__(self,max_threads):
        self.main_url='http://www.sohu.com/'
        self.max_threads=max_threads
        self.thread_manager=ThreadManager(self.max_threads)

    @staticmethod
    def get_url(url):
        doc = pq(url=url)
        for i in doc('a').items():
            item_url=i.attr('href')
            if item_url:
                if item_url.find(host) != -1:
                    if item_url.find('//')==0:
                        item_url='http:'+item_url
                    if item_url[-1]=='/':
                        if visited_queue.count(item_url) or visited_queue.count(item_url[:-1])==0:#http://www.baidu.com 和 http://www.baidu.com/判定为一个
                            url_queue.append(item_url)
                    else:
                        if visited_queue.count(item_url) or visited_queue.count(item_url+'/')==0:
                            url_queue.append(item_url)

    def start(self):
        global proxys
        proxys=Proxy().get_proxys()
        self.get_url(self.main_url)
        visited_queue.append(main_url)#将第一个url加入访问列表
        self.thread_manager.start_all()


class MyThread(threading.Thread):
    def __init__(self,queue):
        self.queue=queue
        self.host = 'www.sohu.com'
        super(MyThread, self).__init__()

    def run(self):
        while self.queue:
            url=self.queue.popleft()
            global count
            print(count)
            count+=1
            if self.is_weak_url(url):
                pass
            else:
                MainManager.get_url(url)

    #http status_code 404或者页面中含有404 not found则为weak_link
    def is_weak_url(self,url):
        visited_queue.append(url)
        try:
            r = requests.get(url=url, headers=headers, timeout=2,proxies={'http':random.choice(proxys)})
            if r.status_code == 404:
                log=Log(url,'404')
                log.wirte()
                return True
            proc = re.compile('404 not found', re.IGNORECASE)
            if proc.search(r.text):
                log = Log(url, '404 not found')
                log.wirte()
                return True
        except Exception as e:
            log = Log(url, e)
            log.wirte()
            return True
        return False


class ThreadManager:
    def __init__(self,max):
        self.max=max
        self.threads=[]

    def start_all(self):
        for i in range(self.max):
            thread = MyThread(url_queue)
            thread.start()
            self.threads.append(thread)

        for item in self.threads:
            item.join()

#错误日志
class Log:
    def __init__(self,url,info):
        self.url=url
        self.info=info
        self.time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def wirte(self):
        print('write '+self.url)
        with open('errors.log','a') as file:
            file.write('time:{}\nurl:{}\ninfo:{}\n\n\n\n'.format(self.time,self.url,self.info))


#代理池获取http://www.xicidaili.com/nn/
class Proxy:
    def __init__(self):
        self.proxys=[]

    def get_proxys(self):
       page=requests.get(url='http://www.xicidaili.com/nn/',headers=headers).text
       proc=re.compile('<tr.*?>.*?<td.*?</td>.*?<td.*?>(.*?)</td>.*?<td.*?>(.*?)</td>.*?<td.*?</td>.*?<td.*?</td>.*?<td.*?>(.*?)</td>.*?</tr>',re.DOTALL)
       if proc.search(page):
           for item in proc.findall(page):
               if(item[2]=='HTTP'):
                   self.proxys.append("{}:{}".format(item[0],item[1]))

       return self.proxys

if __name__ == "__main__":
    manager=MainManager(15)
    manager.start()

