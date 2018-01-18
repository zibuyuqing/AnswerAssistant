# -*- coding: utf-8 -*-

"""

    use adb to capture the phone screen
    then use hanwang text recognize the text
    then use baidu to search answer

"""

from datetime import datetime
import time
import os
from PIL import Image

import sys
reload(sys) # Python2.5 初始化后会删除 sys.setdefaultencoding 这个方法，我们需要重新载入
sys.setdefaultencoding('utf-8')
def analyze_current_screen_text(directory="."):
    """
    capture the android screen now

    :return:
    """
    screenshot_filename = time.time().__str__() + ".png"
    save_text_area = os.path.join(directory, "text_area.png")
    capture_screen(screenshot_filename, directory)
    parse_answer_area(os.path.join(directory, "screenshot.png"),save_text_area)
    return get_area_data(save_text_area)


def capture_screen(filename="screenshot.png", directory="."):
    """
    use adb tools

    :param filename:
    :param directory:
    :return:
    """
    if not os.path.exists(directory):
        os.mkdir(directory)
    os.system("adb shell screencap -p /sdcard/{0}".format(filename))
    os.system("adb pull /sdcard/{0} {1}".format(filename, os.path.join(directory, "screenshot.png")))


def parse_answer_area(source_file, text_area_file):
    """
    crop the answer area

    :return:
    """

    image = Image.open(source_file)
    # adjust it as need
    img_size = image.size
    left = 70
    right = img_size[0] - 70
    top = 350
    bottom = 1300
    region = image.crop((left, top, right, bottom))
    region.save(text_area_file)


def get_area_data(text_area_file):
    """

    :param text_area_file:
    :return:
    """
    with open(text_area_file, "rb") as fp:
        image_data = fp.read()
        return image_data
    return ""