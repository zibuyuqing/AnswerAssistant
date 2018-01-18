# -*- coding: utf-8 -*-

"""

    calculate question and answer relation

    k = count(Q&A) / (count(Q) * count(A))

"""
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

import html5lib
import urllib2
from bs4 import BeautifulSoup
import operator
from functools import partial

from core.baiduzhidao import search_result_number

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def search(question):
    wd = urllib2.quote(u'{0}'.format(question).encode('utf8'))
    url = 'https://zhidao.baidu.com/search?ct=17&pn=0&tn=ikaslist&rn=10&fr=wwwt&word={}'.format(wd)
    result = urllib2.urlopen(url)
    body = BeautifulSoup(result.read(), 'html5lib')
    good_result_div = body.find(class_='list-header').find('dd')
    second_result_div = body.find(class_='list-inner').find(class_='list')
    result_list = []
    if good_result_div is not None:
        good_result = good_result_div.get_text()
        result_list.append(good_result)
        print(good_result.strip())
    if second_result_div is not None:
        second_result_10 = second_result_div.findAll('dl')  # .find(class_='answer').get_text()
        if second_result_10 is not None and len(second_result_10) > 0:
            for index, each_result in enumerate(second_result_10):
                result_dd = each_result.dd.get_text()
                result_list.append(result_dd)
                if index < 3:
                    print(result_dd)
    return result_list
def analyze(result_list,question,keywords_li,is_negate):
    answer_num = len(result_list)
    op_num = len(keywords_li)
    source_arr = []  # 记录各选项得分
    for i in range(0, op_num):
        source_arr.append(0)
    for i in range(0, answer_num):
        result = result_list[i]
        for j in range(0, op_num):
            op = keywords_li[j]
            if op in result:  # 选项在答案中出现一次，加10分
                source_arr[j] += 10
    if len(source_arr) == 0 or max(source_arr) == 0:
        return None
    if is_negate:
        best_index = min(source_arr)
    else:
        best_index = max(source_arr)
    best_result = keywords_li[source_arr.index(best_index)]
    return best_result

