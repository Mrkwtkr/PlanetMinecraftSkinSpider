# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.org/en/latest/topics/items.html

from scrapy import Item, Field


class PmSkinItem(Item):
    # define the fields for your item here like:
    # name = Field()
    title = Field()
    author = Field()
    date = Field()
    raw_url = Field()
    download_url = Field()
    redirect_url = Field()
