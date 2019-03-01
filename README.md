# epaper
运行条件：scrapy + mysql
python版本：3.5
mysql配置文件：epaper/MysqlCoon.py中Config类
根目录下使用： scrapy list 查看所有的爬虫
       使用： scrapy crawl xxx 爬取指定的报刊(需存在对应的数据库表{命名规则：epaper_xxx})