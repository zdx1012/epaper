# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from .MysqlConn import Mysql
import pymysql


class EpaperPipeline(object):
    def process_item(self, item, spider):
        mysql = Mysql()
        sql = ''
        try:
            # BJSpider 新增一个特殊字段
            if spider.name == 'BJSpider':
                sql = "INSERT INTO `epaper_bj`( `title`, `href`, `cType`, `insert_time`, `content`,`send_time`,`lable`) VALUES('%s','%s','%s','%s','%s','%s','%s')" % (
                    pymysql.escape_string(item['title']), item['href'], item['cType'], item['insert_time'], pymysql.escape_string(item['content']),
                    item['send_time'], item['lable'])
            else:
                sql = "INSERT INTO `epaper_%s`( `title`, `href`, `cType`, `insert_time`, `content`,`send_time`) VALUES('%s','%s','%s','%s','%s','%s')" % (
                    spider.name, pymysql.escape_string(item['title']), item['href'], item['cType'], item['insert_time'], pymysql.escape_string(item['content']),
                    item['send_time'])
            mysql.insertOne(sql)
        except BaseException as e:
            print(e.args)
            print(sql)
        mysql.dispose()
        return item
