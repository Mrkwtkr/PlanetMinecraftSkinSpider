# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sqlite3

class SQLitePipeline(object):
	def open_spider(self, spider):
		db_name = spider.settings.get('SQLITE_DB_NAME', 'scrapy_default.db')

		self.db_conn = sqlite3.connect(db_name)
		self.db_cur = self.db_conn.cursor()


	def close_spider(self, spider):
		self.db_conn.commit()
		self.db_conn.close()


	def process_item(self, item, spider):
		self.insert_db(item)

		return item


	def insert_db(self, item):
		values = (
			item['title'],
			item['author'],
			item['date'],
			item['raw_url'],
			item['download_url'],
			item['redirect_url'],
			)
		# 忽略/跳过重复数据
		sql = 'INSERT OR REPLACE INTO skins (title, author, date, raw_url, download_url, redirect_url) VALUES (?,?,?,?,?,?)'
		self.db_cur.execute(sql, values)

		self.db_conn.commit()