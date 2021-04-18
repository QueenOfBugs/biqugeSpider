import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from biqugePro.items import NovelItem, ChapterItem
import re


class BiqugeSpider(CrawlSpider):
    name = 'biquge'
    id = 1
    #  allowed_domains = ['https://www.biquge.info/paihangbang_allvisit/1.html']
    start_urls = ['https://www.biquge.info/paihangbang_allvisit/1.html']
    # 解析分页url的链接提取器
    le_pages = LinkExtractor(restrict_xpaths=('//div[@id="pagelink"]/a'))
    # 解析详情页url的链接提取器
    le_detail = LinkExtractor(restrict_xpaths=(
        '//div[@class="novelslistss"]/ul/li/span[2]/a'))
    # 解析章节内容url的链接提取器
    le_content = LinkExtractor(restrict_xpaths=('//div[@id="list"]/dl/dd/a'))

    rules = (
        # 默认的回调函数是parse,实际调用的还是parse_start_url函数,不指定callback默认的follow是True
        Rule(link_extractor=le_pages, follow=True),
        Rule(link_extractor=le_detail, callback="parse_detail", follow=True),
        Rule(link_extractor=le_content, callback="parse_content", follow=False)
    )

    #  def parse_item(self, response):
    #      item = {}
    #      #item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
    #      #item['name'] = response.xpath('//div[@id="name"]').get()
    #      #item['description'] = response.xpath('//div[@id="description"]').get()
    #      return item
    def parse_detail(self, response):
        # 详情页解析出id,intro,author,title,novel_type
        novel_id = response.request.url.split('/')[-2]
        novel_title = response.xpath('//div[@id="info"]/h1/text()').get()
        novel_author = response.xpath(
            '//div[@id="info"]/p[1]/text()').get().split(':')[-1]
        print(novel_author)
        novel_type = response.xpath(
            '//div[@id="info"]/p[2]/text()').get().split(':')[-1]
        novel_intro = response.xpath('//div[@id="intro"]/p[1]').get()
        item = NovelItem()
        item['novel_id'] = novel_id
        item['novel_title'] = novel_title
        item['novel_author'] = novel_author
        item['novel_type'] = novel_type
        item['novel_intro'] = novel_intro
        item['url'] = response.request.url
        return item

    def parse_content(self, response):
        # 章节页面,选择直接存html文本到数据库
        novel_id = response.request.url.split('/')[-2]
        #  chapter_id = response.request.url.split('/')[-1].split('.')[0]
        novel_content_div = response.xpath('//div[@id="content"]').get()
        pattern = r'<div id=\"content\">(.*)<\/div>'
        chapter_content = re.findall(
            pattern, novel_content_div, re.MULTILINE | re.DOTALL)[0]
        chapter_title = response.xpath('//div[@class="bookname"]/h1/text()').get()
        item = ChapterItem()
        item['novel_id'] = novel_id
        item['chapter_title'] = chapter_title
        item['chapter_content'] = chapter_content
        item['chapter_id'] = self.id
        self.id +=1
        item['url'] = response.request.url
        return item
