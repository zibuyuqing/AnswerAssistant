# -*- coding:utf-8 -*-


"""

    Xi Gua video Million Heroes

"""
import time
from argparse import ArgumentParser

import operator
from functools import partial

from config import app_id
from config import app_key
from config import app_secret
from config import data_directory
from core.android import analyze_current_screen_text
from core.nearby import *
from core.ocr.baiduocr import get_text_from_image as bai_get_text
from core.baiduzhidao import open_webbrowser
import sys
import tkMessageBox as msg
reload(sys) # Python2.5 初始化后会删除 sys.setdefaultencoding 这个方法，我们需要重新载入
sys.setdefaultencoding('utf-8')

negate_word = ['没有', '不是', '不会']
auxiliary_word = ['下列', '以下','哪项','哪个','哪种','谁']
def parse_args():
    parser = ArgumentParser(description="Million Hero Assistant")
    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=5,
        help="default http request timeout"
    )
    return parser.parse_args()


def parse_question_and_answer(text_list):
    question = ""
    start = 0
    for i, keyword in enumerate(text_list):
        question += keyword
        if "?" in keyword:
            start = i + 1
            break

    question = question.split(".")[-1]
    extra_word = negate_word + auxiliary_word
    is_negate = False
    for ele in extra_word:
        if ele in negate_word and ele in question:
            is_negate = True
        if ele in question:
            question = question.replace(ele, '')
    return question, text_list[start:],is_negate


def main():
    print"==" * 50
    args = parse_args()
    timeout = args.timeout
    get_text_from_image = partial(
        bai_get_text,
        app_id=app_id,
        app_key=app_key,
        app_secret=app_secret,
        timeout=timeout)

    start = time.time()
    text_binary = analyze_current_screen_text(
        directory=data_directory
    )
    keywords = get_text_from_image(
        image_data=text_binary,
    )
    if not keywords:
        print("text not recognize")
        return

    question, answers,is_negate = parse_question_and_answer(keywords)

    print("-" * 50)
    print question
    print("-" * 50)
    print("\n".join(answers))
    print "-" * 50, "\n"
    result_list = search(question)
    best_result = analyze(result_list,question,answers,is_negate)
    end = time.time()
    if best_result is None:
        print('\n没有答案')
        open_webbrowser(question)
    else:
        result = "\n" + "=" * 25 + "\n" + "最佳答案是：             " + best_result + "\n" +"=" * 25
        msg.showinfo("答案",result)
if __name__ == "__main__":
    while True:
        print 'please input "Enter" when question appearing and input "q & Enter" to exit'
        go = raw_input()
        if go == 'q':
            break
        main()

