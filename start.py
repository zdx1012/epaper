#!/usr/bin/env python
# -*- coding: utf-8 -*-

if __name__ == '__main__':
    import os

    # os.system('scrapy crawl gjjrb')
    # with open(r'199801_old.txt', mode='r', encoding='gb2312', errors='ignore') as f:
    with open(r'tmp/199804.txt', mode='r', encoding='utf-8') as f:
        c = f.readlines()
    with open(r'tmp/result4.txt', mode='r', encoding='utf-8') as f2:
        d = f2.readlines()
    #     # f2.write(c)
    # print(len(c), len(d))
    for index, lines in enumerate(c):
        if c[index] != d[index]:
            print(c[index])
            print(d[index])
            for index2, tmp in enumerate(c[index]):
                c1 = c[index][index2]
                d1 = d[index][index2]
                if c1 != d1:
                    print(index2, c1, ord(c1), d1, ord(d1))
    #         # print(c[index][index2])
    #         # print(d[index][index2])
    #         # break
