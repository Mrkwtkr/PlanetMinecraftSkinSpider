# -*- coding: utf-8 -*-
import scrapy
import requests
import re

class ImagesSpider(scrapy.Spider):
	name = 'images'
	# 起爬的URL，参考PlanetMinecraft网页，推荐限定一个时间范围爬取
	start_urls = ['https://www.planetminecraft.com/resources/skins/?time_machine=m-0118']
	
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
		# 构造请求头
		headers = {
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
		'accept-encoding': 'gzip, deflate, br',
		'accept-language': 'zh-CN,zh;q=0.9',
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
		}
		# 发送get请求并获取重定向后的Location
		r = requests.get(download_url, headers=headers, timeout=30, allow_redirects=False)
		r.raise_for_status()
		r.encoding = r.apparent_encoding
		if 'Location' in dict(r.headers):
			redirect_url = dict(r.headers)['Location']
		redirect_url = re.search(r'^\S+\.png', redirect_url).group()
		# 导出所需的数据
		yield{
			'title': title,
			'author': author,
			'date': date,
			'raw_url': raw_url,
			'download_url': download_url,
			'redirect_url': redirect_url,
		}
		# with open('download_urls.csv', encoding='utf-8') as f:
		# 	f.write('%s,\n')


	def parse(self, response):
		# 定位页面中的皮肤发布帖
		post_urls = response.xpath('//div[@class="resource_block"]//a[@class="r-title"]/@href').extract()
		for i in post_urls:
			post_url = response.urljoin(i)
			yield scrapy.Request(post_url, callback=self.postparse)
		# 寻找下一页并跳转，持续爬取
		next_url = response.xpath('//a[@class="pagination_next"]/@href').extract_first()
		if next_url is not None:
			next_url = response.urljoin(next_url)
			yield scrapy.Request(next_url, callback=self.parse)