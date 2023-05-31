#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2023/5/22 22:02
# @Author  : Smalltown
# @FileName: utils.py
# @Software: PyCharm
import os

def writefileJson(page_number,data,dictory):
    # 构建文件名
    # 构建文件路径和名称
    filename = os.path.join(dictory, f"action_page{page_number}.txt")

    # 写入文件
    with open(filename, "wb") as file:
        file.write(data)

    print(f"数据已成功写入文件：{filename}")

def writefileLink(page_number, linklist,dictory):
    # 构建文件名
    # 构建文件路径和名称
    filename = os.path.join(dictory, f"action_page{page_number}.txt")

    # 打开文件并写入URL
    with open(filename, 'w') as file:
        for url in linklist:
            file.write(url + '\n')



def readfileLink(page_number_start=0,page_number_finish=1, dictory='link'):
    '''    page_number_start = 0
        page_number_finish = 1
        dictory = 'link'
        url_link = utils.readfileLink(page_number_start, page_number_finish, dictory)
        print(url_link)'''

    url_list = []

    for page_number in range(page_number_start, page_number_finish + 1):
        file_name = os.path.join(dictory, f"action_page{page_number}.txt")
        with open(file_name, 'r') as file:
            urls = file.read().splitlines()
            url_list.extend(urls)

    return url_list