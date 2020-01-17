import requests
from lxml import etree
import sys
import time

sys.path.append('../../../')
from config import TIMELIMIT_REIMU, MAXINFO_REIMU
from kth_timeoutdecorator import *

async def from_reimu_get_info(key_word: str) -> str:
    if "miku" in key_word.lower():
        print("[warning]Taboo words are being triggered")
        return None
    repass = ""
    url = 'https://blog.reimu.net/search/' + key_word
    try:
        print("[info]Now starting get the {}".format(url))
        repass = await get_repass(url)
    except TimeoutException as e:
        print("[warning] {}".format(e))
    
    return repass

@timeout(TIMELIMIT_REIMU)
async def get_repass(url: str) -> str:
    repass = ""
    info = "————————————————\n注意大部分资源解压密码为⑨\n————————————————\n"
    fund = None
    html_data = requests.get(url)
    html = etree.HTML(html_data.text)
    
    fund = html.xpath('//h1[@class="page-title"]/text()')[0]
    if fund == "未找到":
        return "老司机也找不到路了……"

    headers = html.xpath('//article/header/h2/a/text()')
    urls = html.xpath('//article/header/h2/a/@href')
    print("[info]Now get {} post from search page".format(len(headers)))

    headers_d = []
    urls_d = []
    for i, header in enumerate(headers):
        if "音乐" not in header:
            headers_d.append(headers[i])
            urls_d.append(urls[i])
        else: print("[info]This title {} does not meet the requirements".format(header))

    header_len = len(headers_d)
    print("[info]Get {} post after processing".format(header_len))
    if header_len > MAXINFO_REIMU:
        headers_d = headers_d[:MAXINFO_REIMU]
        urls_d = urls_d[:MAXINFO_REIMU]

    for h_s, url_s in zip(headers_d, urls_d):
        if h_s != "审核结果存档":
            time.sleep(1.5)
            putline = await get_son_html_info(h_s, url_s)
            if putline:
                if repass:
                    repass = "\n\n- - - - - - - - \n".join([repass, putline])
                else:
                    repass = putline
        else: print("[info]审核归档页面已跳过")

    if repass:
        repass = info + repass
    return repass

async def get_son_html_info(h_s, url_s) -> str:
    repass = ""
    print("[info]Now starting get the {}".format(url_s))
    html_data = requests.get(url_s)
    html = etree.HTML(html_data.text)
    pres = html.xpath('//div[@class="entry-content"]/pre/text()')
    a_texts = html.xpath('//div[@class="entry-content"]/pre//a/text()')
    a_hrefs = html.xpath('//div[@class="entry-content"]/pre//a/@href')

    if pres and a_texts and a_hrefs:
        while "" in pres:
            pres.remove("")
        
        repass = "【资源名称】 {}\n\n{}".format(h_s, pres[0].strip())
        for i, (a_t_s, a_h_s) in enumerate(zip(a_texts, a_hrefs)):
            a = "\n {}  {}  {} ".format(a_t_s, a_h_s, pres[i+1].strip())
            repass += a
    else: print("[warning]Not get putline from {}".format(url_s))

    return repass