import requests
from pyquery import PyQuery as pq
import json
import argparse


class Video(object):
    def __init__(self,name,see,intro):
        self.name=name
        self.see=see
        self.intro=intro

    def __str__(self):
        return '''
        名称:{}
        播放量:{}
        简介:{}
        '''.format(self.name,self.see,self.intro)


class bilibili(object):
    recent_url = "https://bangumi.bilibili.com/api/timeline_v2_global"  # 最近更新
    detail_url = "https://bangumi.bilibili.com/anime/{season_id}"

    def __init__(self):
        self.dom=pq(requests.get('https://bangumi.bilibili.com/22/').text)

    def get_recent(self,num):
        '''最近更新'''
        items=json.loads(requests.get(self.recent_url).text)['result']
        videos=[]
        for i in items:
            name=i['title']
            link=self.detail_url.format(season_id=i['season_id'])
            d=pq(requests.get(url=link).text)
            see = d(".info-count .info-count-item").eq(1).find('em').text()
            intro = d('.info-desc-wrp').find('.info-desc').text()
            videos.append(Video(name=name,see=see,intro=intro))
        if num==0:
            for item in videos:
                print(item)
        else:
            for item in videos[:num]:
                print(item)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--recent',help="get the recent info",action="store_true")
    parser.add_argument('--num',help="The number of results returned,default show all",type=int,default=0)
    parser.add_argument('-v','--version',help="show version",action="store_true")
    args=parser.parse_args()

    if args.version:
        print("bilibili 1.0")
    elif args.recent:
       b = bilibili()
       b.get_recent(args.num)

