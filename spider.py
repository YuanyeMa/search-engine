# 网络爬虫程序，主要完成从指定URL开始递归下载相关网页操作。

import argparse
import requests
from collections import deque 
import re
from bs4 import BeautifulSoup

url_cnt=0

def analyze_web(queue, visited, content, parent_url):
    global url_cnt
    # step 1: 提取出页面内所有的链接，并加入队列
    # pattern = re.compile(r'<a href=\"([0-9a-zA-Z\_\/\.\%\?\=\-\&\:]+)\"> target=\"_blank\"', re.I)
    pattern = re.compile(r'<a href=\"([0-9a-zA-Z\_\/\.\%\?\=\-\&\:]+)\">', re.I)
    urls = pattern.findall(content)
    print("共找到"+str(len(urls))+"个url")
    
    for url in urls:
        if not re.match(r'http', url):
            #print(url)
            #print(parent_url)
            url = parent_url+url
        if (url not in queue) and (url not in visited):
            queue.append(url)
            url_cnt=url_cnt+1
            print(url)

    # step 2: 解析网页内容，并建立索引

    pass


def main():
    parse =  argparse.ArgumentParser(description="递归下载指定URL的网页")
    parse.add_argument("url", type=str, help="seed url")

    args = parse.parse_args()

    seed_url = args.url

    queue = deque() # 存储待搜索的url
    queue.append(seed_url)

    visited = set() # 存储已经访问过的url

    while queue and (url_cnt<10000) :
        url = queue.popleft()
        print(url)
        visited.add(url)

        try:
            res = requests.get(url)
        except:
            print("open url failed!")
            continue
        
        content = res.text
        analyze_web(queue, visited, content, url)

    print("共找到%s个url"% (url_cnt))
       



if __name__ == '__main__':
    main()
