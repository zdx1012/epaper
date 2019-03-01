# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EpaperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    cType = scrapy.Field()  # 报社名
    insert_time = scrapy.Field()  # 插入时间
    title = scrapy.Field()  # 标题
    content = scrapy.Field()  # 内容
    href = scrapy.Field()  # 链接
    send_time = scrapy.Field()  # 发布时间
    lable = scrapy.Field()  # 标签(北京晚报独有)
