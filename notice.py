from bs4 import BeautifulSoup
import requests
import re
import time
import random

def get_one_page(url):
    headers = {
        "User-Agent" : "'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'",
    }
    response = requests.get(url=url, headers=headers,verify=False)
    response.encoding = response.apparent_encoding 
    soup = BeautifulSoup(response.text, "html.parser")
    return soup
    # retry_count = 5
    # proxy = get_proxy().get("proxy")
    # while retry_count > 0:
    #     try:
    #         response = requests.get(url=url, proxies={"http": "http://{}".format(proxy)}, headers=headers,verify=False)
    #         response.encoding = response.apparent_encoding 
    #         soup = BeautifulSoup(response.text, "html.parser")
    #         return soup
    #     except Exception as e:
    #         retry_count -= 1
    # delete_proxy(proxy)
    # return None

def parser_page(soup):
    title = '# ' + soup.find(name='h1', attrs={"class": "zg_Htitle"}).text
    time = '### 发布时间：' + soup.select_one('div[class="zg_time"] em').text
    source = '### ' +  soup.select_one('div[class="zg_time"] font').text
    content = soup.select('div[class="offcn_shocont"] p')
    pre = re.compile('(\d+)[人|名]')
    number = pre.search(title)
    person = '### 招聘人数：' +  number[0] if number else ''
    register_time = '### 报名时间：'
    register_type = '### 报名方式：'
    ri_time_pr = re.compile('(报名).?时间：(?P<time>.*)')
    ri_type_pr = re.compile('.*?[线上|网上|网络报名].*')
    for i in content:
        ri_type = ri_type_pr.search(i.text)
        ri_time = ri_time_pr.search(i.text)
        register_type += '网上报名' if ri_type else '线下报名'
        if ri_time:
            register_time += ri_time.group('time')
        break
    notice = [title, time, source, person, register_time, register_type, '\n'.join('%s'%num for num in content)]
    return notice

def write_file(notice, type):
    file_name = notice[0]
    file_name = file_name.replace('#', '')
    file_name = file_name.replace('"', '＂')
    file_name = re.sub(r'[\\\>\<\|\:\*\?\/]', '、', file_name)
    print(file_name)
    path = './file/'+ type + '/' + file_name.strip() + '.md'
    with open(path, 'w', encoding='utf-8') as f:
        f.write("\n".join(notice))

def get_url_list(page, date='2020-01-01', type=''):
    if type=='gwy':
        li = page.select('div[class="lh_Hotrecommend"] li')
    else:
        li = page.select('ul[class="lh_newBobotm02"] li')
    # print(li)
    hrefs = []
    for i in li:
        href = i.select('a')[1].get('href')
        date1 = i.select_one('span').text
        if date <= date1:
            hrefs.append(href)
    return hrefs

def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json()

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

def main():
    type = 'gwy' # teacher|sydw|gwy
    date = '2020-01-01'
    pre_url = ''
    if type == 'gwy':
        # 公务员
        pre_url = 'http://www.offcn.com/gwy/kaoshi/zhaokao/'
    elif type == 'sydw':
        # 事业单位
        pre_url = 'http://www.offcn.com/sydw/kaoshi/2139/'
    elif type == 'teacher':
        # 教师招聘
        pre_url = 'http://www.offcn.com/jiaoshi/zhaopin/2240/'
    for i in range(0, 1):
        url ='{pre_url}{html}'.format(pre_url=pre_url,html=(str(i)+'.html') if i else '')
        list_soup = get_one_page(url)
        urls = get_url_list(list_soup, date, type)
        # print(urls)
        for i in urls:
            time.sleep(random.randint(1,3))
            soup = get_one_page(i)
            return_list = parser_page(soup)
            write_file(return_list, type)
            

if __name__ == "__main__":
    main()
    # get_proxy().get('proxy')