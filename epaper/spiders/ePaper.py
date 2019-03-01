# -*- coding: utf-8 -*-

from ..items import EpaperItem
from scrapy import Request
from scrapy.spiders import Spider
import datetime
import traceback
from urllib import parse
import re


def create_assist_date(datestart=None, dateend=None, add_day=1, sep=('-', '/')):
    """
    创建日期递增的列表
    :param datestart: 起始日期 20180101
    :param dateend: 结束日期 20190101
    :param add_day: 递增日期 1
    :param sep: 年月日之间的分隔符
    :return:
    """
    # 创建日期辅助表

    if datestart is None:
        datestart = '2016-01-01'
    if dateend is None:
        dateend = datetime.datetime.now().strftime('%Y-%m-%d')

    # 转为日期格式
    datestart = datetime.datetime.strptime(datestart, '%Y-%m-%d')
    dateend = datetime.datetime.strptime(dateend, '%Y-%m-%d')
    date_list = [datestart.strftime('%Y{0}%m{1}%d').format(sep[0], sep[1])]

    while datestart < dateend:
        # 日期叠加
        datestart += datetime.timedelta(days=+add_day)
        # 日期转字符串存入列表
        date_list.append(datestart.strftime('%Y{0}%m{1}%d').format(sep[0], sep[1]))
    return date_list


# 光明日报（2008-2019）
class GMRBSpider(Spider):
    name = 'GMRBpaper'
    allowed_domains = ['epaper.gmw.cn']
    start_date = '2008-01-01'
    end_date = '2019-01-04'

    # end_date = datetime.datetime.now().strftime('%Y-%m-%d')

    # 生成不同日期的链接
    def start_requests(self):
        # 新闻页码 示例链接：http://epaper.gmw.cn/gmrb/html/2019-01/04/nbs.D110000gmrb_02.htm#
        for date in create_assist_date(datestart=self.start_date, dateend=self.end_date):
            yield Request('http://epaper.gmw.cn/gmrb/html/{0}/nbs.D110000gmrb_01.htm'.format(date))

    # 解析版面目录
    def parse(self, response):

        page_data = response.xpath('//*[@id="pageLink"]/@href').extract()
        for page in page_data:
            base_url = str(response.url).rsplit('nbs')[0]
            cur_page_url = base_url + page
            yield Request(cur_page_url, callback=self.parse_left_url, meta={'base_url': base_url})

    # 解析左侧链接
    def parse_left_url(self, response):
        article_urls = response.xpath('//*[@id="titleList"]/ul/li/a/@href').extract()
        for url in article_urls:
            content_url = response.meta['base_url'] + url
            yield Request(content_url, callback=self.parse_content)

    # 解析内容
    def parse_content(self, response):
        item = EpaperItem()

        try:
            title = response.xpath("/html/body/div[6]/div[2]/div[3]/div/h1/text()").extract_first()
            p_list = response.xpath('//*[@id="articleContent"]/p//text()').extract()
            content = "\n".join(p_list).replace('\xa0', '')  # 替换原文中的空格(&nbsp)
            if len(content) == 0:
                div_list = response.xpath('//*[@id="articleContent"]//text()').extract()
                content = "\n".join(div_list).replace('\xa0', '')

            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content.strip()
            item['href'] = response.url
            item['cType'] = '光明日报'
            item['send_time'] = str(response.url).split('_')[1]
        except BaseException as e:
            print(e.args)
            print(traceback.print_exc())
        if len(item['content']) > 100:
            return item


# 人民日报（2018-2019）
class RMRBSpider(Spider):
    name = 'RMRBpaper'
    allowed_domains = ['paper.people.com.cn']
    start_date = '2018-01-01'
    end_date = '2019-01-04'

    # end_date = datetime.datetime.now().strftime('%Y-%m-%d')

    # 生成不同日期的链接
    def start_requests(self):
        # 新闻页码 示例链接：http://epaper.gmw.cn/gmrb/html/2019-01/04/nbs.D110000gmrb_02.htm#
        for date in create_assist_date(datestart=self.start_date, dateend=self.end_date):
            yield Request('http://paper.people.com.cn/rmrb/html/{0}/nbs.D110000renmrb_01.htm'.format(date))

    # 解析版面目录
    def parse(self, response):

        page_data = response.xpath('//*[@id="pageLink"]/@href').extract()
        for page in page_data:
            base_url = str(response.url).rsplit('nbs')[0]
            cur_page_url = base_url + page
            yield Request(cur_page_url, callback=self.parse_left_url, meta={'base_url': base_url})

    # 解析左侧链接
    def parse_left_url(self, response):
        article_urls = response.xpath('//*[@id="titleList"]/ul/li/a/@href').extract()
        for url in article_urls:
            content_url = response.meta['base_url'] + url
            yield Request(content_url, callback=self.parse_content)

    # 解析内容
    def parse_content(self, response):
        item = EpaperItem()

        try:
            title = response.xpath("/html/body/div[1]/div/div[2]/div[4]/div/h1/text()").extract_first()
            p_list = response.xpath('//*[@id="articleContent"]/p//text()').extract()
            content = "\n".join(p_list).replace('\xa0', '')  # 替换原文中的空格(&nbsp)
            if len(content) == 0:
                div_list = response.xpath('//*[@id="articleContent"]//text()').extract()
                content = "\n".join(div_list).replace('\xa0', '')

            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content.strip()
            item['href'] = response.url
            item['cType'] = '人民日报'
            item['send_time'] = str(response.url).split('_')[1]
        except BaseException as e:
            print(e.args)
            print(traceback.print_exc())
        if len(item['content']) > 100:
            return item


# 北京晚报（2017-2019）
class BJSpider(Spider):
    # http://bjwb.bjd.com.cn/html/2019-01/08/node_113.htm
    # http://bjwb.bjd.com.cn/html/2019-01/01/content_570345.htm
    name = 'BJSpider'
    start_date = '2017-01-01'
    end_date = '2019-01-21'

    # 生成不同日期的链接
    def start_requests(self):
        # 新闻页码 示例链接：http://epaper.gmw.cn/gmrb/html/2019-01/04/nbs.D110000gmrb_02.htm#
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)
        for date in date_list:
            yield Request('http://bjwb.bjd.com.cn/html/{0}/node_113.htm'.format(date), dont_filter=True)

    # 解析不同版面
    def parse(self, response):
        res = response.xpath('//div[@class="hidenPage"]/li/a/@href').extract()
        res_lable = response.xpath('//div[@class="hidenPage"]/li/a/text()').extract()
        for index, tmp in enumerate(res):
            url = parse.urljoin(response.url, tmp)
            lable = re.sub('\(.*?\)', '', res_lable[index])
            yield Request(url, callback=self.parse_layout, dont_filter=True, meta={'lable': lable})

    def parse_layout(self, response):
        res = response.xpath('//*[@id="list"]/div[2]/ul/li/h2/a/@href').extract()
        for index, tmp in enumerate(res):
            url = parse.urljoin(response.url, tmp)
            yield Request(url, callback=self.parse_content, dont_filter=True, meta=response.meta)

    def parse_content(self, response):
        content_list = response.xpath('//div[@class="text"]//text()').extract()
        content = "\n".join(content_list).replace('\xa0', '').strip()

        title_list = response.xpath('//*[@id="list"]/div/h2/text()|//*[@id="list"]/div/h1/text()').extract()
        title = ''.join(title_list).strip().replace('\r\n', '').replace('\t', '').replace('\r', '')

        day = ''.join(response.xpath('//*[@id="list"]/div/div[1]/span[2]/text()').extract()).strip()
        day = re.sub(re.compile('\D'), '', day)

        item = EpaperItem()
        item['title'] = title
        item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['content'] = content
        item['href'] = response.url
        item['cType'] = '北京晚报'
        item['send_time'] = day
        item['lable'] = response.meta['lable']
        # print(response.url)
        if len(title) > 0 and len(content) > 100:
            yield item


# 新京报
class BjnewsSpider(Spider):
    name = 'bjnews'
    allowed_domains = ['epaper.bjnews.com.cn']

    start_date = '2012-01-01'
    end_date = '2019-02-23'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)
        for date in date_list:
            yield Request('http://epaper.bjnews.com.cn/html/{0}/node_1.htm'.format(date), dont_filter=True)

    # 解析版面
    def parse(self, response):
        link_list = response.xpath('//*[@id="pageLink"]/@href').extract()
        for link in link_list:
            new_url = parse.urljoin(response.url, link)
            yield Request(new_url, callback=self.parse_layout, dont_filter=True)

    def parse_layout(self, response):
        news_link_list = response.xpath('//area/@href').extract()
        for news_link in news_link_list:
            news_link = str(parse.urljoin(response.url, news_link)).split('?')[0]
            yield Request(news_link, callback=self.parse_content)

    # 解析内容
    def parse_content(self, response):
        title = response.xpath('/html/body/div[2]/div[2]/h1/text()').extract_first()
        content_list = response.xpath('//founder-content//text()').extract()
        content = ''.join(content_list).strip()
        day = re.sub(re.compile('\D'), '', str(response.url).rsplit('_')[0])

        if title and content and len(title) > 0 and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '新京报'
            item['send_time'] = day
            yield item


# 新民晚报(分词中)
class XmwbSpider(Spider):
    name = 'xmwb'
    allowed_domains = ['xmwb.xinmin.cn']
    start_date = '2012-01-01'
    end_date = '2019-02-25'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)
        for date in date_list:
            yield Request('http://xmwb.xinmin.cn/html/{0}/node_1.htm'.format(date), dont_filter=True)

    # 解析不同的版面
    def parse(self, response):
        link_list = response.xpath('//td[@class="default"]/a[@id="pageLink"]/@href').extract()
        for link in link_list:
            new_link = parse.urljoin(response.url, link)
            yield Request(new_link, callback=self.parsr_layout, dont_filter=True)

    def parsr_layout(self, response):
        news_link_list = response.xpath('//*[@id="main-ed-articlenav-list"]/table//a/@href').extract()
        for news_link in news_link_list:
            content_link = parse.urljoin(response.url, news_link)
            # 当为报头版面时，不进行任何处理
            if 'content_1_9.htm' not in content_link:
                yield Request(content_link, callback=self.parse_cotent, dont_filter=True)

    # 解析内容
    def parse_cotent(self, response):
        # print(response.url)
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        try:
            title = response.xpath('//*[@id="article-title"]/founder-title/text()').extract()[1]
        except BaseException as e:
            title = ''
        content_list = response.xpath('//*[@id="ozoom"]//text()').extract()
        content = ''.join(content_list).strip()
        # 特殊版面(广告、本报信息) 不处理
        if title and content and len(title) > 0 and len(content) > 100 and title not in ['广告', '本报信息']:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '新民晚报'
            item['send_time'] = day
            yield item


# 羊城晚报
class YcwbSpider(Spider):
    name = 'ycwb'
    allowed_domains = ['ep.ycwb.com']
    start_date = '2017-01-01'
    end_date = '2019-02-24'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)
        for date in date_list:
            yield Request('http://ep.ycwb.com/epaper/ycwb/html/{0}/index.htm'.format(date), dont_filter=True)

    def parse(self, response):
        left_link_list = response.xpath('/html/body/div[1]/div/div[5]/ul/li/div/ul/li/a')
        for link in left_link_list:
            text = link.xpath('text()').extract_first()  # 提取a标签文字
            link = link.xpath('@href').extract_first()
            new_link = parse.urljoin(response.url, str(link))
            if '彩票' in text or '体彩' in text or '广告' in text:
                pass
            else:
                yield Request(new_link, callback=self.parse_layout, dont_filter=True)

    def parse_layout(self, response):
        news_link_list = response.xpath('//*[@id="list"]/div[2]/ul/li/h2/a/@href').extract()
        for news_link in news_link_list:
            news_link = parse.urljoin(response.url, news_link)
            yield Request(news_link, callback=self.parse_cotent, dont_filter=True)

    def parse_cotent(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url).rsplit('_')[0])
        title = response.xpath('//*[@id="list"]/div/h1/text()').extract_first()

        content_list = response.xpath('//*[@id="list"]/div/div[2]/p/text()').extract()
        content = ''.join(content_list[0:-1]).strip()

        epaper_type = response.xpath('//*[@id="list"]/div/div[1]/span[1]/text()').extract_first()
        if epaper_type:
            cType = epaper_type[3:]
        else:
            cType = ''

        # 特殊版面(广告、本报信息) 不处理
        if title and content and len(title) > 0 and len(content) > 100 and title not in ['广告', '本报信息']:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = cType
            item['send_time'] = day
            yield item


# 经济日报
class JjrbSpider(Spider):
    name = 'jjrb'
    allowed_domains = ['paper.ce.cn']
    # http://paper.ce.cn/jjrb/html/2008-01/27/node_2.htm#
    start_date = '2008-01-27'
    end_date = '2019-02-24'
    # end_date = '2008-02-27'
    handle_httpstatus_list = [404]

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)
        for date in date_list:
            yield Request('http://paper.ce.cn/jjrb/html/{0}/node_2.htm'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//td[@class="default"]/a[@id="pageLink"]/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_layout, dont_filter=True)

    def parse_layout(self, response):
        # print(response.url, '-----')
        news_link_list = response.xpath('//td[@class="default"]/a[starts-with(@href,"content_")]/@href').extract()
        # print(news_link_list)
        for link in news_link_list:
            url = parse.urljoin(response.url, link)
            # print(url)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = response.xpath('//td[@class="STYLE32"]//td[@class="font01"]/text()').extract_first()

        content_list = response.xpath('//div[@id="ozoom"]//text()').extract()
        content = ''.join(content_list).strip()

        # 特殊版面(广告、本报信息) 不处理
        if title and content and len(title) > 0 and len(content) > 100 and title not in ['广告', '本报信息']:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '经济日报'
            item['send_time'] = day
            yield item


# 证券时报
# 4个不同的日期分隔点 网页布局不同
# http://epaper.stcn.com/paper/zqsb/html/2008-05/14/node_2.htm 左侧栏
# http://epaper.stcn.com/paper/zqsb/html/2011-01/04/node_2.htm  弹窗
# http://epaper.stcn.com/paper/zqsb/html/2012-02/07/node_2.htm  #  点击跳转链接
# http://epaper.stcn.com/paper/zqsb/html/2016-07/22/node_2.htm  #  点击弹窗--更新版
class ZqsbSpider(Spider):
    name = 'zqsb'
    allowed_domains = ['epaper.stcn.com']
    custom_settings = {
        'REDIRECT_ENABLED': False,
    }
    # start_date = '2016-07-22'
    start_date = '2008-05-14'
    end_date = '2019-02-24'

    # end_date = '2016-07-22'

    def opinion_date(self, url):
        date = int(re.sub(re.compile('\D'), '', url[39:50]))
        if date < 20110104:
            return 1
        elif date < 20120207:
            return 2
        elif date < 20160722:
            return 3
        else:
            return 4

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)
        for date in date_list:
            url = 'http://epaper.stcn.com/paper/zqsb/html/{0}/node_2.htm'.format(date)
            type = self.opinion_date(url)
            yield Request(url, dont_filter=True, meta={'type': type})

    def parse(self, response):
        ctype = int(response.meta['type'])
        if ctype == 1:
            model_links = response.xpath('//td[@class="default"]/a[@id="pageLink"]/@href').extract()
        elif ctype == 2 or ctype == 3:
            # 该类型 可直接获取到内容链接
            content_links = response.xpath('//div[@id="listWrap"]/div/ul/li/a/@href').extract()
            for link in content_links:
                url = parse.urljoin(response.url, link)
                yield Request(url, callback=self.parse_content, dont_filter=True, meta=response.meta)
            model_links = []
        elif ctype == 4:
            content_links = response.xpath('//*[@id="webtree"]/dl/dd/ul/li/a/@href').extract()
            for link in content_links:
                url = parse.urljoin(response.url, link)
                yield Request(url, callback=self.parse_content, dont_filter=True, meta=response.meta)
            model_links = []
        else:
            model_links = []
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_layout, dont_filter=True, meta=response.meta)

    def parse_layout(self, response):
        ctype = int(response.meta['type'])
        if ctype == 1:
            news_link_list = response.xpath('//td[@class="default"]/a[starts-with(@href,"content_")]/@href').extract()
            for link in news_link_list:
                url = parse.urljoin(response.url, link)
                yield Request(url, callback=self.parse_content, dont_filter=True, meta=response.meta)

    def parse_content(self, response):
        ctype = int(response.meta['type'])
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        if ctype == 1:
            title = response.xpath('//td[@class="font01"]/strong/text()').extract_first()
            content_list = response.xpath('//div[@id="ozoom"]//text()').extract()
            content = ''.join(content_list).strip()
        elif ctype == 2 or ctype == 3:
            title = response.xpath('//*[@id="mainTiile"]/h2/text()').extract_first()
            content_list = response.xpath('//div[@id="mainCon"]/div/founder-content//text()').extract()
            content = ''.join(content_list).strip()
        elif ctype == 4:
            title = response.xpath('/html/body/div[1]/p/text()').extract_first()
            content_list = response.xpath('/html/body/div[2]/div/founder-content//text()').extract()
            content = ''.join(content_list).strip()
        else:
            title, content = '', ''
        if title and title not in ['导读', '今日导读', '特别提示', '今日公告导读'] and content and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '证券时报'
            item['send_time'] = day
            yield item


# 扬子晚报
class YzwbSpider(Spider):
    name = 'yzwb'
    allowed_domains = ['epaper.yzwb.net']
    # http://epaper.yzwb.net/html_t/2012-06/14/node_1.htm
    start_date = '2012-06-14'
    end_date = '2019-02-25'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)
        for date in date_list:
            yield Request('http://epaper.yzwb.net/html_t/{0}/node_1.htm'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//*[@id="navigation"]/ul/li/a/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_layout, dont_filter=True)

    def parse_layout(self, response):
        news_link_list = response.xpath('//*[starts-with(@id,"mp")]/a/@href').extract()
        for link in news_link_list:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = response.xpath('//td[@class="title1"]/text()').extract_first()

        content_list = response.xpath('//div[@id="ozoom"]//text()').extract()
        content = ''.join(content_list).strip()
        if title and content and len(title) > 0 and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '扬子晚报'
            item['send_time'] = day
            yield item


# 人民日报海外版
class Rmrb_hw(Spider):
    name = 'rmrb_hw'
    # http://paper.people.com.cn/rmrbhwb/html/2014-07/09/node_865.htm
    allowed_domains = ['paper.people.com.cn']
    # start_date = '2008-06-12'
    start_date = '2008-06-12'
    # end_date = '2019-02-25'
    end_date = '2019-02-26'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)
        for date in date_list:
            yield Request('http://paper.people.com.cn/rmrbhwb/html/{0}/node_865.htm'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//a[@id="pageLink"]/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_layout, dont_filter=True)

    def parse_layout(self, response):
        news_link_list = response.xpath('//div[@id="titleList"]/ul/li/a/@href').extract()
        for link in news_link_list:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = response.xpath('//div[@class="text_c"]/h1/text()').extract_first()

        content_list = response.xpath('//div[@id="ozoom"]//p//text()').extract()
        content = ''.join(content_list).strip()
        if title and content and len(title) > 0 and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '人民日报海外版'
            item['send_time'] = day
            # print(title, response.url, content)
            yield item


# 国际金融报
class GjjrbSpider(Spider):
    name = 'gjjrb'
    # http://paper.people.com.cn/gjjrb/html/2019-02/18/node_645.htm
    allowed_domains = ['paper.people.com.cn']
    start_date = '2008-06-16'
    end_date = '2019-02-25'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)

        for date in date_list:
            yield Request('http://paper.people.com.cn/gjjrb/html/{0}/node_645.htm'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//a[@id="pageLink"]/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_layout, dont_filter=True)

    def parse_layout(self, response):
        news_link_list = response.xpath('//div[@id="titleList"]/ul/li/a/@href').extract()
        for link in news_link_list:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = response.xpath('//div[@class="text_c"]/h1/text()').extract_first()

        content_list = response.xpath('//div[@id="ozoom"]//p//text()').extract()
        content = ''.join(content_list).strip()
        if title and content and len(title) > 0 and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '国际金融报'
            item['send_time'] = day
            # print(title, response.url, content)
            yield item


# 中国能源报
class ZgnybSpider(Spider):
    name = 'zgnyb'
    # http://paper.people.com.cn/zgnyb/html/2009-04/06/node_2222.htm#
    allowed_domains = ['paper.people.com.cn']
    start_date = '2009-04-06'
    end_date = '2019-02-26'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)
        for date in date_list:
            yield Request('http://paper.people.com.cn/zgnyb/html/{0}/node_2222.htm#'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//a[@id="pageLink"]/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_layout, dont_filter=True)

    def parse_layout(self, response):
        news_link_list = response.xpath('//div[@id="titleList"]/ul/li/a/@href').extract()
        for link in news_link_list:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = response.xpath('//div[@class="text_c"]/h1/text()').extract_first()

        content_list = response.xpath('//div[@id="ozoom"]//p//text()').extract()
        content = ''.join(content_list).strip()
        if title and content and len(title) > 0 and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '中国能源报'
            item['send_time'] = day
            # print(title, response.url, content)
            yield item


# 健康时报
class JksbSpider(Spider):
    name = 'jksb'
    # http://paper.people.com.cn/jksb/html/2008-06/16/node_811.htm
    allowed_domains = ['paper.people.com.cn']
    start_date = '2008-06-16'
    end_date = '2019-02-26'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)

        for date in date_list:
            yield Request('http://paper.people.com.cn/jksb/html/{0}/node_811.htm'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//a[@id="pageLink"]/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_layout, dont_filter=True)

    def parse_layout(self, response):
        news_link_list = response.xpath('//div[@id="titleList"]/ul/li/a/@href').extract()
        for link in news_link_list:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = response.xpath('//div[@class="text_c"]/h1/text()').extract_first()

        content_list = response.xpath('//div[@id="ozoom"]//p//text()').extract()
        content = ''.join(content_list).strip()
        if title and content and len(title) > 0 and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '健康时报'
            item['send_time'] = day
            # print(title, response.url, content)
            yield item


# 讽刺与幽默
class FcyymSpider(Spider):
    name = 'fcyym'
    # http://paper.people.com.cn/fcyym/html/2012-03/09/node_841.htm
    allowed_domains = ['paper.people.com.cn']
    start_date = '2012-03-09'
    end_date = '2019-02-26'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)

        for date in date_list:
            yield Request('http://paper.people.com.cn/fcyym/html/{0}/node_841.htm'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//a[@id="pageLink"]/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_layout, dont_filter=True)

    def parse_layout(self, response):
        news_link_list = response.xpath('//div[@id="titleList"]/ul/li/a/@href').extract()
        for link in news_link_list:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = response.xpath('//div[@class="text_c"]/h1/text()').extract_first()

        content_list = response.xpath('//div[@id="ozoom"]//p//text()').extract()
        content = ''.join(content_list).strip()
        if title and content and len(title) > 0 and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '讽刺与幽默'
            item['send_time'] = day
            # print(title, response.url, content)
            yield item


# 中国城市报
class ZgcsSpider(Spider):
    name = 'zgcs'
    # http://paper.people.com.cn/zgcsb/html/2015-02/02/node_2591.htm
    allowed_domains = ['paper.people.com.cn']
    start_date = '2015-02-02'
    end_date = '2019-02-26'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)

        for date in date_list:
            yield Request('http://paper.people.com.cn/zgcsb/html/{0}/node_2591.htm'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//a[@id="pageLink"]/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_layout, dont_filter=True)

    def parse_layout(self, response):
        news_link_list = response.xpath('//div[@id="titleList"]/ul/li/a/@href').extract()
        for link in news_link_list:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = response.xpath('//div[@class="text_c"]/h1/text()').extract_first()

        content_list = response.xpath('//div[@id="ozoom"]//p//text()').extract()
        content = ''.join(content_list).strip()
        if title and content and len(title) > 0 and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '中国城市报'
            item['send_time'] = day
            # print(title, response.url, content)
            yield item


# ---------------------------------------------------------------

# 新闻战线
class XwzxSpider(Spider):
    name = 'xwzx'
    # http://paper.people.com.cn/xwzx/html/2007-12/10/node_922.htm
    allowed_domains = ['paper.people.com.cn']
    start_date = '2007-12-02'
    end_date = '2019-02-26'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)

        for date in date_list:
            yield Request('http://paper.people.com.cn/xwzx/html/{0}/node_922.htm'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//div[@id="titleList"]/ul/li/a/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = response.xpath('//div[@class="text_c"]/h1/text()').extract_first()

        content_list = response.xpath('//div[@id="ozoom"]//p//text()').extract()
        content = ''.join(content_list).strip()
        if title and content and len(title) > 0 and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '新闻战线'
            item['send_time'] = day
            # print(title, response.url, content)
            yield item


# 环球人物
class HqrwSpider(Spider):
    name = 'hqrw'
    # http://paper.people.com.cn/hqrw/html/2011-10/26/node_1122.htm
    allowed_domains = ['paper.people.com.cn']
    start_date = '2011-10-26'
    end_date = '2019-02-26'

    # end_date = '2011-12-26'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)

        for date in date_list:
            yield Request('http://paper.people.com.cn/hqrw/html/{0}/node_1122.htm'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//div[@id="titleList"]/ul/li/a/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = response.xpath('//div[@class="text_c"]/h1/text()').extract_first()

        content_list = response.xpath('//div[@id="ozoom"]//p//text()').extract()
        content = ''.join(content_list).strip()
        if title and content and len(title) > 0 and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '环球人物'
            item['send_time'] = day
            # print(title, response.url, content)
            yield item


# 人民论坛
class RmltSpider(Spider):
    name = 'rmlt'
    # http://paper.people.com.cn/rmlt/html/2018-03/11/node_1222.htm
    allowed_domains = ['paper.people.com.cn']
    start_date = '2018-03-11'
    end_date = '2019-02-26'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)

        for date in date_list:
            yield Request('http://paper.people.com.cn/rmlt/html/{0}/node_1222.htm'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//div[@id="titleList"]/ul/li/a/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = response.xpath('//div[@class="text_c"]/h1/text()').extract_first()

        content_list = response.xpath('//div[@id="ozoom"]//p//text()').extract()
        content = ''.join(content_list).strip()
        if title and content and len(title) > 0 and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '人民论坛'
            item['send_time'] = day
            # print(title, response.url, content)
            yield item


# 人民周刊
class RmzkSpider(Spider):
    name = 'rmzk'
    # http://paper.people.com.cn/rmzk/html/2015-08/01/node_2651.htm#
    allowed_domains = ['paper.people.com.cn']
    start_date = '2015-08-01'
    end_date = '2019-02-26'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)

        for date in date_list:
            yield Request('http://paper.people.com.cn/rmzk/html/{0}/node_2651.htm'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//div[@id="titleList"]/ul/li/a/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = response.xpath('//div[@class="text_c"]/h1/text()').extract_first()

        content_list = response.xpath('//div[@id="ozoom"]//p//text()').extract()
        content = ''.join(content_list).strip()
        if title and content and len(title) > 0 and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '人民周刊'
            item['send_time'] = day
            # print(title, response.url, content)
            yield item


# 中国经济周刊
class ZgjjzkSpider(Spider):
    name = 'zgjjzk'
    # http://paper.people.com.cn/zgjjzk/html/2009-01/05/node_1422.htm
    allowed_domains = ['paper.people.com.cn']
    start_date = '2009-01-05'
    end_date = '2019-02-26'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)

        for date in date_list:
            yield Request('http://paper.people.com.cn/zgjjzk/html/{0}/node_1422.htm'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//div[@id="titleList"]/ul/li/a/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = response.xpath('//div[@class="text_c"]/h1/text()').extract_first()

        content_list = response.xpath('//div[@id="ozoom"]//p//text()').extract()
        content = ''.join(content_list).strip()
        if title and content and len(title) > 0 and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '中国经济周刊'
            item['send_time'] = day
            # print(title, response.url, content)
            yield item


# 新安全
class XaqSpider(Spider):
    name = 'xaq'
    # http://paper.people.com.cn/xaq/html/2012-01/02/node_2262.htm
    allowed_domains = ['paper.people.com.cn']
    start_date = '2012-01-02'
    end_date = '2019-02-26'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)

        for date in date_list:
            yield Request('http://paper.people.com.cn/xaq/html/{0}/node_2262.htm'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//div[@id="titleList"]/ul/li/a/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = response.xpath('//div[@class="text_c"]/h1/text()').extract_first()

        content_list = response.xpath('//div[@id="ozoom"]//p//text()').extract()
        content = ''.join(content_list).strip()
        if title and content and len(title) > 0 and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '新安全'
            item['send_time'] = day
            # print(title, response.url, content)
            yield item


# 民生周刊
class MszkSpider(Spider):
    name = 'mszk'
    # http://paper.people.com.cn/mszk/html/2010-09/20/node_1622.htm
    allowed_domains = ['paper.people.com.cn']
    start_date = '2010-09-20'
    end_date = '2019-02-26'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)

        for date in date_list:
            yield Request('http://paper.people.com.cn/mszk/html/{0}/node_1622.htm'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//div[@id="titleList"]/ul/li/a/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = response.xpath('//div[@class="text_c"]/h1/text()').extract_first()

        content_list = response.xpath('//div[@id="ozoom"]//p//text()').extract()
        content = ''.join(content_list).strip()
        if title and content and len(title) > 0 and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '民生周刊'
            item['send_time'] = day
            # print(title, response.url, content)
            yield item


# 中国报业
class ZgbySpider(Spider):
    name = 'zgby'
    # http://paper.people.com.cn/zgby/html/2015-08/15/node_2751.htm
    allowed_domains = ['paper.people.com.cn']
    start_date = '2015-08-15'
    end_date = '2019-02-26'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)

        for date in date_list:
            yield Request('http://paper.people.com.cn/zgby/html/{0}/node_2751.htm'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//div[@id="titleList"]/ul/li/a/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = response.xpath('//div[@class="text_c"]/h1/text()').extract_first()

        content_list = response.xpath('//div[@id="ozoom"]//p//text()').extract()
        content = ''.join(content_list).strip()
        if title and content and len(title) > 0 and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '中国报业'
            item['send_time'] = day
            # print(title, response.url, content)
            yield item


# ----------------------------------------------

# 深圳特区报
class SztqbSpider(Spider):
    name = 'sztqb'
    # http://sztqb.sznews.com/PC/layout/201705/01/colA01.html
    allowed_domains = ['sztqb.sznews.com']
    start_date = '2018-05-01'
    end_date = '2019-02-26'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date, sep=('', '/'))

        for date in date_list:
            # http://sztqb.sznews.com/PC/layout/201803/21/colA01.html
            # http://sztqb.sznews.com/PC/layout/201803/22/node_A01.html
            # 不同日期的起始链接不同
            if int(re.sub(re.compile(r'\D+'), '', date)) < 20180322:
                yield Request('http://sztqb.sznews.com/PC/layout/{0}/colA01.html'.format(date), dont_filter=True)
            else:
                yield Request('http://sztqb.sznews.com/PC/layout/{0}/node_A01.html'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//div[@class="Therestlist"]/ul/li/a[not(@class="restmask")]/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_layout, dont_filter=True)

    def parse_layout(self, response):
        news_link_list = response.xpath('//div[@class="newslist"]/ul/li/h3/a/@href').extract()
        for link in news_link_list:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = response.xpath('//*[@id="ScroLeft"]/div[1]/h3/text()').extract_first()

        content_list = response.xpath('//*[@id="ScroLeft"]/div[2]/founder-content/p//text()').extract()
        content = ''.join(content_list).strip()
        if title and content and len(title) > 0 and len(content) > 100 and '广告' not in title:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '深圳特区报'
            item['send_time'] = day
            # print(title, response.url, content)
            yield item


# 深圳商报
class SzsbSpider(Spider):
    name = 'szsb'
    allowed_domains = ['szsb.sznews.com']
    start_date = '2017-05-01'
    end_date = '2019-02-26'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date, sep=('', '/'))

        for date in date_list:
            # http://szsb.sznews.com/PC/layout/201803/21/colA01.html
            # http://szsb.sznews.com/PC/layout/201803/22/node_A01.html
            # 不同日期的起始链接不同
            if int(re.sub(re.compile(r'\D+'), '', date)) < 20180322:
                yield Request('http://szsb.sznews.com/PC/layout/{0}/colA01.html'.format(date), dont_filter=True)
            else:
                yield Request('http://szsb.sznews.com/PC/layout/{0}/node_A01.html'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//div[@class="Therestlist"]/ul/li/a[not(@class="restmask")]/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_layout, dont_filter=True)

    def parse_layout(self, response):
        news_link_list = response.xpath('//div[@class="newslist"]/ul/li/h3/a/@href').extract()
        for link in news_link_list:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = response.xpath('//*[@id="ScroLeft"]/div[1]/h3/text()').extract_first()

        content_list = response.xpath('//*[@id="ScroLeft"]/div[2]/founder-content/p//text()').extract()
        content = ''.join(content_list).strip()
        if title and content and len(title) > 0 and len(content) > 100 and '广告' not in title:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '深圳商报'
            item['send_time'] = day
            # print(title, response.url, content)
            yield item


# 深圳晚报
class SzwbSpider(Spider):
    name = 'szwb'
    allowed_domains = ['wb.sznews.com']
    start_date = '2017-05-02'
    end_date = '2019-02-27'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date, sep=('', '/'))

        for date in date_list:
            # http://wb.sznews.com/PC/layout/201803/21/colA01.html
            # http://wb.sznews.com/PC/layout/201803/22/node_A01.html
            # 不同日期的起始链接不同
            if int(re.sub(re.compile(r'\D+'), '', date)) < 20180322:
                yield Request('http://wb.sznews.com/PC/layout/{0}/colA01.html'.format(date), dont_filter=True)
            else:
                yield Request('http://wb.sznews.com/PC/layout/{0}/node_A01.html'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//div[@class="Therestlist"]/ul/li/a[not(@class="restmask")]/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_layout, dont_filter=True)

    def parse_layout(self, response):
        news_link_list = response.xpath('//div[@class="newslist"]/ul/li/h3/a/@href').extract()
        for link in news_link_list:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = response.xpath('//*[@id="ScroLeft"]/div[1]/h3/text()').extract_first()

        content_list = response.xpath('//*[@id="ScroLeft"]/div[2]/founder-content/p//text()').extract()
        content = ''.join(content_list).strip()
        if title and content and len(title) > 0 and len(content) > 100 and '广告' not in title:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '深圳晚报'
            item['send_time'] = day
            # print(title, response.url, content)
            yield item


# 晶报
class JbSpider(Spider):
    name = 'jb'
    # http://jb.sznews.com/PC/layout/201705/02/colA01.html
    allowed_domains = ['wb.sznews.com']
    start_date = '2017-05-02'
    end_date = '2019-02-27'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date, sep=('', '/'))

        for date in date_list:
            # http://jb.sznews.com/PC/layout/201803/21/colA01.html
            # http://jb.sznews.com/PC/layout/201803/22/node_A01.html
            # 不同日期的起始链接不同
            if int(re.sub(re.compile(r'\D+'), '', date)) < 20180322:
                yield Request('http://jb.sznews.com/PC/layout/{0}/colA01.html'.format(date), dont_filter=True)
            else:
                yield Request('http://jb.sznews.com/PC/layout/{0}/node_A01.html'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//div[@class="Therestlist"]/ul/li/a[not(@class="restmask")]/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_layout, dont_filter=True)

    def parse_layout(self, response):
        news_link_list = response.xpath('//div[@class="newslist"]/ul/li/h3/a/@href').extract()
        for link in news_link_list:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = response.xpath('//*[@id="ScroLeft"]/div[1]/h3/text()').extract_first()

        content_list = response.xpath('//*[@id="ScroLeft"]/div[2]/founder-content/p//text()').extract()
        content = ''.join(content_list).strip()
        if title and content and len(title) > 0 and len(content) > 100 and '广告' not in title:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '晶报'
            item['send_time'] = day
            # print(title, response.url, content)
            yield item


# 深圳教育时报
class SzjySpider(Spider):
    name = 'szjy'
    # http://szjy.sznews.com/PC/layout/201706/02/col01.html
    allowed_domains = ['szjy.sznews.com']
    start_date = '2016-06-02'
    end_date = '2019-02-27'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date, sep=('', '/'))

        for date in date_list:
            # http://szjy.sznews.com/PC/layout/201803/21/colA01.html
            # http://szjy.sznews.com/PC/layout/201803/22/node_A01.html
            # 不同日期的起始链接不同
            if int(re.sub(re.compile(r'\D+'), '', date)) < 20180322:
                yield Request('http://szjy.sznews.com/PC/layout/{0}/col01.html'.format(date), dont_filter=True)
            else:
                yield Request('http://szjy.sznews.com/PC/layout/{0}/node_01.html'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//div[@class="Therestlist"]/ul/li/a[not(@class="restmask")]/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_layout, dont_filter=True)

    def parse_layout(self, response):
        news_link_list = response.xpath('//div[@class="newslist"]/ul/li/h3/a/@href').extract()
        for link in news_link_list:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = response.xpath('//*[@id="ScroLeft"]/div[1]/h3/text()').extract_first()

        content_list = response.xpath('//*[@id="ScroLeft"]/div[2]/founder-content/p//text()').extract()
        content = ''.join(content_list).strip()
        if title and content and len(title) > 0 and len(content) > 100 and '广告' not in title:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '深圳教育'
            item['send_time'] = day
            # print(title, response.url, content)
            yield item


# 宝安日报
class BarbSpider(Spider):
    name = 'barb'
    # http://barb.sznews.com/PC/layout/201706/01/colA01.html
    allowed_domains = ['barb.sznews.com']
    start_date = '2017-06-01'
    end_date = '2019-02-27'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date, sep=('', '/'))

        for date in date_list:
            # http://barb.sznews.com/PC/layout/201803/21/colA01.html
            # http://barb.sznews.com/PC/layout/201803/22/node_A01.html
            # 不同日期的起始链接不同
            if int(re.sub(re.compile(r'\D+'), '', date)) < 20180322:
                yield Request('http://barb.sznews.com/PC/layout/{0}/colA01.html'.format(date), dont_filter=True)
            else:
                yield Request('http://barb.sznews.com/PC/layout/{0}/node_A01.html'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//div[@class="Therestlist"]/ul/li/a[not(@class="restmask")]/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            if not str(url).endswith('.pdf'):
                yield Request(url, callback=self.parse_layout, dont_filter=True)

    def parse_layout(self, response):
        news_link_list = response.xpath('//div[@class="newslist"]/ul/li/h3/a/@href').extract()
        for link in news_link_list:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = response.xpath('//*[@id="ScroLeft"]/div[1]/h3/text()').extract_first()

        content_list = response.xpath('//*[@id="ScroLeft"]/div[2]/founder-content/p//text()').extract()
        content = ''.join(content_list).strip()
        if title and content and len(title) > 0 and len(content) > 100 and '广告' not in title:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '宝安日报'
            item['send_time'] = day
            # print(title, response.url, content)
            yield item


# -----------------------------
# 今晚报
class JwbSpider(Spider):
    name = 'jwb'
    # http://epaper.jwb.com.cn/jwb/html/2015-06/08/node_1.htm
    allowed_domains = ['epaper.jwb.com.cn']
    start_date = '2015-06-08'
    # end_date = '2015-06-08'
    end_date = '2019-02-28'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)

        for date in date_list:
            # 生成起始链接
            yield Request('http://epaper.jwb.com.cn/jwb/html/{0}/node_1.htm'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//*[@id="bmdhTable"]/tbody/tr/td/a[@class="rigth_bmdh_href"]/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_layout, dont_filter=True)

    def parse_layout(self, response):
        news_link_list = response.xpath('//tr[@class="wzlb_tr"]/td[@class="default"]/div/a/@href').extract()
        for link in news_link_list:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = str(response.xpath('//p[@class="BSHARE_TEXT"]/text()').extract_first()).strip().replace('\n', ' ')
        content_list = response.xpath('//div[@id="ozoom"]//text()').extract()
        content = ''.join(content_list).strip()

        if title and content and len(title) > 0 and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '今晚报'
            item['send_time'] = day
            # print(title, response.url, content)
            yield item


# 渤海早报
class BhzbSpider(Spider):
    name = 'bhzb'
    # http://epaper.jwb.com.cn/bhzb/html/2015-07/13/node_1.htm
    allowed_domains = ['epaper.jwb.com.cn']
    start_date = '2015-07-13'
    # end_date = '2015-07-13'
    end_date = '2019-02-28'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)

        for date in date_list:
            # 生成起始链接
            yield Request('http://epaper.jwb.com.cn/bhzb/html/{0}/node_1.htm'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//*[@id="bmdhTable"]/tbody/tr/td/a[@class="rigth_bmdh_href"]/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_layout, dont_filter=True)

    def parse_layout(self, response):
        news_link_list = response.xpath('//tr[@class="wzlb_tr"]/td[@class="default"]/div/a/@href').extract()
        for link in news_link_list:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = str(response.xpath('//p[@class="BSHARE_TEXT"]/text()').extract_first()).strip().replace('\n', ' ')
        content_list = response.xpath('//div[@id="ozoom"]//text()').extract()
        content = ''.join(content_list).strip()

        if title and content and len(title) > 0 and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '渤海早报'
            item['send_time'] = day
            # print(title, response.url, content)
            yield item


# 今晚经济周报
class JwjjzbSpider(Spider):
    name = 'jwjjzb'
    # http://epaper.jwb.com.cn/jwjjzb/html/2015-07/10/node_1.htm
    allowed_domains = ['epaper.jwb.com.cn']
    start_date = '2015-07-10'
    # end_date = '2015-07-10'
    end_date = '2019-02-27'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)

        for date in date_list:
            # 生成起始链接
            yield Request('http://epaper.jwb.com.cn/jwjjzb/html/{0}/node_1.htm'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//*[@id="bmdhTable"]/tbody/tr/td/a[@class="rigth_bmdh_href"]/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_layout, dont_filter=True)

    def parse_layout(self, response):
        news_link_list = response.xpath('//tr[@class="wzlb_tr"]/td[@class="default"]/div/a/@href').extract()
        for link in news_link_list:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = str(response.xpath('//p[@class="BSHARE_TEXT"]/text()').extract_first()).strip().replace('\n', ' ')
        content_list = response.xpath('//div[@id="ozoom"]//text()').extract()
        content = ''.join(content_list).strip()

        if title and content and len(title) > 0 and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '今晚经济周刊'
            item['send_time'] = day
            # print(title, response.url, content)
            yield item


# 中老年时报
class ZlnsbSpider(Spider):
    name = 'zlnsb'
    # http://epaper.jwb.com.cn/zlnsb/html/2015-09/14/node_1.htm
    allowed_domains = ['epaper.jwb.com.cn']
    start_date = '2015-09-14'
    # end_date = '2015-07-10'
    end_date = '2019-02-28'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)

        for date in date_list:
            # 生成起始链接
            yield Request('http://epaper.jwb.com.cn/zlnsb/html/{0}/node_1.htm'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//*[@id="bmdhTable"]/tbody/tr/td/a[@class="rigth_bmdh_href"]/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_layout, dont_filter=True)

    def parse_layout(self, response):
        news_link_list = response.xpath('//tr[@class="wzlb_tr"]/td[@class="default"]/div/a/@href').extract()
        for link in news_link_list:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = str(response.xpath('//p[@class="BSHARE_TEXT"]/text()').extract_first()).strip().replace('\n', ' ')
        content_list = response.xpath('//div[@id="ozoom"]//text()').extract()
        content = ''.join(content_list).strip()

        if title and content and len(title) > 0 and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '中老年时报'
            item['send_time'] = day
            # print(title, response.url, content)
            yield item


# 中国技术市场报
class ZgjsscbSpider(Spider):
    name = 'zgjsscb'
    # http://epaper.jwb.com.cn/zgjsscb/html/2015-08/21/node_1.htm
    allowed_domains = ['epaper.jwb.com.cn']
    start_date = '2015-08-21'
    end_date = '2019-02-28'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)

        for date in date_list:
            # 生成起始链接
            yield Request('http://epaper.jwb.com.cn/zgjsscb/html/{0}/node_1.htm'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//*[@id="bmdhTable"]/tbody/tr/td/a[@class="rigth_bmdh_href"]/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_layout, dont_filter=True)

    def parse_layout(self, response):
        news_link_list = response.xpath('//tr[@class="wzlb_tr"]/td[@class="default"]/div/a/@href').extract()
        for link in news_link_list:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = str(response.xpath('//p[@class="BSHARE_TEXT"]/text()').extract_first()).strip().replace('\n', ' ')
        content_list = response.xpath('//div[@id="ozoom"]//text()').extract()
        content = ''.join(content_list).strip()

        if title and content and len(title) > 0 and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '中国技术市场报'
            item['send_time'] = day
            # print(title, response.url, content)
            yield item


# ----------------------------------------------------------------------------------------
# 南方日报
# 已知的有2种网页布局，因不确定是哪一天网页布局更改，故写了2种xpath路径
class NfrbSpider(Spider):
    name = 'nfrb'
    allowed_domains = ['epaper.southcn.com']
    # start_date = '2010-05-20'
    # end_date = '2010-05-20'
    start_date = '2007-12-01'
    end_date = '2019-02-27'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)
        for date in date_list:
            # 生成起始链接
            yield Request('http://epaper.southcn.com/nfdaily/html/{0}/node_2.htm'.format(date), dont_filter=True)

    def parse(self, response):
        # 直接处理新闻链接 http://epaper.southcn.com/nfdaily/html/2017-03/09/node_2.htm
        news_links = response.xpath('//*[@id="mCSB_4"]/div[1]/ul/li/div/a/@href').extract()
        if len(news_links) > 0:
            for link in news_links:
                url = parse.urljoin(response.url, link)
                yield Request(url, callback=self.parse_content, dont_filter=True)
        else:
            # 解析不同版面，再处理新闻
            model_links = response.xpath('//td[@class="default"]/a[@id="pageLink" or @id="pagelink"]/@href').extract()
            for link in model_links:
                url = parse.urljoin(response.url, link)
                yield Request(url, callback=self.parse_layout, dont_filter=True)

    def parse_layout(self, response):
        # 2个xpath路径，可提取网站改版前后的新闻链接地址
        news_link_list = response.xpath('//td[@class="default"]/a[starts-with(@href,"content_")]/@href').extract()  # 旧版
        if len(news_link_list) == 0:
            news_link_list = response.xpath('//*[@id="artPList1"]/li/a/@href').extract()  # 新版

        for link in news_link_list:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        # 旧版
        title = response.xpath('//td[@class="font01"]/text()').extract_first()
        content_list = response.xpath('//*[@id="ozoom"]//text()').extract()
        content = ''.join(content_list).strip()
        content = re.sub(re.compile(r'\s'), ' ', str(content))
        if title is None:
            # 新版
            title = response.xpath('//div[@id="print_area"]/h1/text()').extract_first()
            content_list = response.xpath('//*[@id="content"]//text()').extract()
            content = ''.join(content_list).strip()

        if title and content and len(title) > 0 and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '南方日报'
            item['send_time'] = day
            # print(title, day, response.url, content, '----------------------')
            yield item


# 成都商报
class CdsbSpider(Spider):
    name = 'cdsb'
    start_date = '2012-05-01'
    end_date = '2019-02-28'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date, add_day=90)
        for date in date_list:
            # 生成起始链接
            yield Request('http://e.chengdu.cn/html/{0}/node_2.htm'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//a[@id="pageLink"]/@href').extract()
        for link in model_links:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_layout, dont_filter=True)

    def parse_layout(self, response):
        # 旧版
        news_link_list = response.xpath('//div[@class="sidebar-content"]/ul/li/a/@href').extract()
        if len(news_link_list) == 0:
            # 新版
            news_link_list = response.xpath('//*[@id="nowPageArticleList"]/li/a/@href').extract()

        for link in news_link_list:
            url = parse.urljoin(response.url, link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        # 旧版 和 新版 的xpath路径相同
        title = response.xpath('//div[@class="content-title"]/h4/text()').extract_first()
        content_list = response.xpath('//td[@class="xilan_content_tt"]//text()').extract()
        content = ''.join(content_list).strip()

        if title and content and len(title) > 0 and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '成都商报'
            item['send_time'] = day
            # print(title, day, content)
            yield item


# 南方都市报
class NfdsbSpider(Spider):
    name = 'nfdsb'
    start_date = '2017-10-16'
    # end_date = '2017-10-16'
    # start_date = '2019-02-28'
    end_date = '2019-02-28'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)
        for date in date_list:
            # 生成起始链接
            yield Request('http://epaper.oeeee.com/epaper/A/html/{0}/index.htm'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//div[@class="shortcutbox"]/ul/li[1]/div/ul/li/a/@href').extract()
        for link in model_links:
            url = response.urljoin(link)
            yield Request(url, callback=self.parse_layout, dont_filter=True)

    def parse_layout(self, response):
        news_link_list = response.xpath('//div[@class="main-list"]//a/@href').extract()
        for link in news_link_list:
            url = response.urljoin(link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        # 旧版
        title = response.xpath('//div[@class="article"]/h1/text()').extract_first()
        content_list = response.xpath('//div[@class="text"]//text()').extract()
        content = ''.join(content_list).strip()
        content = re.sub(re.compile(r'\s'), ' ', str(content))
        if title and content and len(title) > 0 and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '南方都市报'
            item['send_time'] = day
            print(title, day, response.url, content, '--------------------')
            # yield item


# 南方农村报
class NfncSpider(Spider):
    name = 'nfnc'
    start_date = '2017-05-18'
    end_date = '2019-02-28'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date, sep=('', ''))
        for date in date_list:
            # 生成起始链接
            yield Request('http://epaper.nfncb.cn/nfnc/content/{0}/Page01TB.htm'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//ul[@class="ul_1"]/li/a/@href').extract()
        for link in model_links:
            url = response.urljoin(link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = response.xpath('//div[@class="news_title"]/h1/text()').extract_first()
        content_list = response.xpath('//div[@class="contenttext"]//text()').extract()
        content = ''.join(content_list).strip()
        if title and content and len(title) > 0 and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '南方农村报'
            item['send_time'] = day
            # print(title, day, response.url, content, '--------------------')
            yield item


# 21世纪经济报
# http://epaper.21jingji.com/html/2014-09/02/node_1.htm#
class SjjjSpider(Spider):
    name = 'sjjj'
    start_date = '2014-09-02'
    # end_date = '2014-09-02'
    end_date = '2019-02-28'

    def start_requests(self):
        date_list = create_assist_date(datestart=self.start_date, dateend=self.end_date)
        for date in date_list:
            # 生成起始链接
            yield Request('http://epaper.21jingji.com/html/{0}/node_1.htm'.format(date), dont_filter=True)

    def parse(self, response):
        model_links = response.xpath('//div[@class="news_list"]/ul/li/a/@href').extract()
        for link in model_links:
            url = response.urljoin(link)
            yield Request(url, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        # print(response.url)
        day = re.sub(re.compile('\D'), '', str(response.url))[:8]
        title = response.xpath('//h1[@class="news_title"]/text()').extract_first()
        content_list = response.xpath('//div[@id="news_text"]/p//text()').extract()
        content = ''.join(content_list).strip()
        if title and content and len(title) > 0 and len(content) > 100:
            item = EpaperItem()
            item['title'] = title
            item['insert_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['content'] = content
            item['href'] = response.url
            item['cType'] = '21世纪经济报'
            item['send_time'] = day
            # print(title, day, response.url, content, '--------------------')
            yield item
