# -*- coding: utf-8 -*-
import scrapy
import requests
import re
from ..items import PmSkinItem

class ImagesSpider(scrapy.Spider):
    name = 'images'
    # 起爬的URL，参考PlanetMinecraft网页，推荐限定一个时间范围爬取
    start_urls = []
    # 取1~12整数，构造起爬的URL
    for i in range(1, 13):
        if len(str(i)) == 1:
            i = '0%s' % i
        # 爬取指定年%s月的页面
        base_url = 'https://www.planetminecraft.com/resources/skins/?time_machine=m-%s17' % i
        start_urls.append(base_url)
    
    # 重定向的解析函数
    def redirect_parse(self, response):
        item = response.meta['key']
        print('[<<<<<response.url>>>>>] %s' % response.url)
        redirect_url = re.search(r'^(\S+\.png?)\?', response.url).group(1)
        item['redirect_url'] = redirect_url
        yield item


    # 皮肤发布帖的解析函数
    def postparse(self, response):
        # 提取发布日期、作者和帖子链接
        title = re.search(r'/skin/(\S+)/$', response.url).group(1)
        # 有的帖子中皮肤存在多次更新，日期取匹配列表中的最后一项
        date = response.xpath('//div[@class="post_date txt-subtle"]/abbr[@class="comment-date timeago"]/@title').re(r'\d+-\d+-\d+')[-1]
        author = response.xpath('//*[@id="resource_object"]/div[3]/div[1]/a[2]/text()').extract_first()
        raw_url = response.url
        # 提取初步的下载地址
        download_url = response.xpath('//a[@title="Download "]/@href').extract_first()
        download_url = response.urljoin(download_url)
        # 将获取的数据存入定义好的Item
        item = PmSkinItem()
        item['title'] = title
        item['author'] = author
        item['date'] = date
        item['raw_url'] = raw_url
        item['download_url'] = download_url
        yield scrapy.Request(download_url, meta={'key':item}, callback=self.redirect_parse)


    def parse(self, response):
        # 定位页面中的皮肤发布帖
        post_urls = response.xpath('//div[@class="resource_block"]//a[@class="r-title"]/@href').extract()
        for i in post_urls:
            post_url = response.urljoin(i)
            yield scrapy.Request(post_url, callback=self.postparse)
        # 寻找下一页并跳转，持续爬取
        next_url = response.xpath('//a[@class="pagination_next"]/@href').extract_first()
        if next_url is not None:
            page_priority = int(re.search(r'p=(\d+)', next_url).group(1))
            next_url = response.urljoin(next_url)
            yield scrapy.Request(next_url, callback=self.parse, priority=page_priority)
        else:
            print('[<<<<<未找到下一页>>>>>]')
            view(response)
