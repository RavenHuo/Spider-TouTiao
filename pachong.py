import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import json
import re
import threading

def get_page_index(offset,keyword):
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'cur_tab':'1',

    }
    url='http://www.toutiao.com/search_content/?'+urlencode(data)

    try:
        html = requests.get(url)
        if html.status_code == 200:
            return html.text
        else:
            return None
    except RequestException:
        print('失败')
        return None

def parser_page_index(html):
    data=json.loads(html)
    if data and 'data' in data.keys():#if data!=0 and 'data'in data,keys()
        for item in data.get('data'):#遍历data内的data
            yield item.get('article_url')#geturl

def get_page_detail(url):
    try:
        html = requests.get(url)
        if html.status_code == 200:
            return html.text
        else:
            return None
    except RequestException:
        print('失败')
        return None



def parser_url_detail(html):
    image1_pattern=re.compile('gallery: (.*?);',re.S)
    image2_pattern = re.compile('artilceInfo:(.*?)}', re.S)
    result1=re.search(image1_pattern,html)
    result2=re.search(image2_pattern,html)
    if result1:
        data1=(result1.group(1))
        url1_pattern=re.compile('"url_list":.{"url":"(.*?)"',re.S)
        url1=re.findall(url1_pattern,data1)
        if url1:
            return url1
    elif result2:
        data2 = (result2.group(1))
        url2_pattern = re.compile('img src=&quot;(.*?)&quot', re.S)
        url2 = re.findall(url2_pattern, data2)
        if url2:
            return url2


def saveImage(html,result):
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find('title').getText()
    i=0
    if result:
        for url in result:
            imagesurl = imageurl(url)
            image=requests.get(imagesurl)
            if image.status_code==200:
                i+=1
                j=str(i)
                open(title+j+''+'.jpg','wb').write(image.content)
                print(title+'第'+j+'张图片已经下载完成')
    print('所有图片已经下载完成')


def imageurl(url):
    if 'origin' in url:
        key1=re.compile('com(.*?)origin..',re.S)
        key2=re.compile('http:(.*?)p',re.S)
        imagesurl1=re.sub(key1,'com/origin/',url)
        imagesurl11=re.sub(key2,'http://p',imagesurl1)
        return imagesurl11
    #elif 'large' in url:
     #   key2=re.compile('(.*?)large...',re.S)
      #  imagesurl2=re.sub(key2,'http://p3.pstatp.com/large/',url)
       # return imagesurl2
    else:
        return url

def running():
    html = get_page_index(page, '街拍')
    for url in parser_page_index(html):
        html = get_page_detail(url)
        if html:
            result = parser_url_detail(html)
            saveImage(html, result)

class Mythread(threading.Thread):
    def run(self):
        running()
    def __init__(self,page):
        threading.Thread.__init__(self)
        self.page=page




if __name__ == '__main__':
    thread=[5]
    for i in range(0,2):
        page=i*20
        thread[i]=Mythread(page)
        thread[i].start()
