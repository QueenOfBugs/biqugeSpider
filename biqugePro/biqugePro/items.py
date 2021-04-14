# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BiqugeproItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class NovelItem(scrapy.Item):
    novel_id = scrapy.Field()
    novel_title = scrapy.Field()
    novel_author = scrapy.Field()
    novel_type = scrapy.Field()
    novel_intro = scrapy.Field()
    url = scrapy.Field()

class ChapterItem(scrapy.Item):
    novel_id = scrapy.Field()
    chapter_content = scrapy.Field()
    chapter_title = scrapy.Field()
    chapter_id = scrapy.Field()
    url = scrapy.Field()

