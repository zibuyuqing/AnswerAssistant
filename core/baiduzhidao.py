# -*- coding: utf-8 -*-

"""

    Baidu zhidao searcher

"""



import requests
from lxml import html
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import sys
import webbrowser
reload(sys) # Python2.5 初始化后会删除 sys.setdefaultencoding 这个方法，我们需要重新载入
sys.setdefaultencoding('utf-8')
def zhidao_search(keyword, default_answer_select, timeout=2):
    """
    Search BaiDu zhidao net

    :param keyword:
    :param timeout:
    :return:
    """
    answer_url_li = parse_search(
        keyword=keyword,
        default_answer_select=default_answer_select,
        timeout=timeout)
    return parse_answer(answer_url_li)


def get_general_number(result):
    for item in ("百度", "为", "您", "找到", "相关", "结果", "约", "个", ","):
        result = result.replace(item, "")
    return result

def open_webbrowser(question):
    webbrowser.open('https://baidu.com/s?wd=' + question)
def search_result_number(keyword, timeout=2):
    """
    Search keyword and get search number

    :param keyword:
    :param timeout:
    :return:
    """
    url = "http://www.baidu.com/s"
    params = {
        "wd": keyword.encode("gbk")
    }
    resp = requests.get(url, params=params, timeout=timeout)
    if not resp.ok:
        print("baidu search error")
        return 0
    parser = html.fromstring(resp.text)
    result = parser.xpath("//div[@class='nums']/text()")
    if not result:
        return 0

    return int(get_general_number(result[0]))


def parse_search(keyword, default_answer_select=2, timeout=2):
    """
    Parse BaiDu zhidao search

    only return the first `default_answer_select`

    :param keyword:
    :param default_answer_select:
    :return:
    """
    params = {
        "lm": "0",
        "rn": "10",
        "pn": "0",
        "fr": "search",
        "ie": "gbk",
        "word": keyword.encode("gbk")
    }

    url = "https://zhidao.baidu.com/search"
    resp = requests.get(url, params=params, timeout=timeout)
    if not resp.ok:
        print("baidu zhidao api error")
        return ""
    parser = html.fromstring(resp.text)
    question_li = parser.xpath("//*[@id='page-main']//div[@class='list-inner']/*[@id='wgt-list']/dl/dt/a/@href")
    return question_li[:default_answer_select]


def parse_answer(urls, timeout=2):
    def fetch(url):
        resp = requests.get(url, timeout=timeout)
        if not resp.ok:
            return ""
        if resp.encoding == "ISO-8859-1" or not resp.encoding:
            resp.encoding = requests.utils.get_encodings_from_content(resp.text)[0]
        return resp.text

    final = []
    with ThreadPoolExecutor(5) as executor:
        future_to_url = {
            executor.submit(fetch, url): url
            for url in urls
        }

        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                text = future.result()
                parser = html.fromstring(text)
                parts = parser.xpath(
                    "//*[contains(@id, 'best-answer')]//*[@class='line content']/*[contains(@id, 'best-content')]/text()")
                if not parts:
                    parts = parser.xpath(
                        "//*[@id='wgt-answers']//*[contains(@class, 'answer-first')]//*[contains(@id, 'answer-content')]//span[@class='con']/text()")
                final.append(" ".join(parts))
            except Exception as exc:
                print("get url: {0} error: {1}".format(url, str(exc)))

    return final
