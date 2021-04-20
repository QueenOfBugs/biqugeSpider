# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql


def clean_data(item):
    for k in item.keys():
        item[k] = str(item[k]).replace('\'', '').replace('\"', '')


class BiqugeproPipeline:
    def open_spider(self, spider):
        print("爬虫开始")
        # 打卡数据库连接
        self.fp = open('fail_urls', 'a')
        self.connect = pymysql.Connect(
            #  host='127.0.0.1', port=3306, user='root', password='kamisama', db='spider'
            host='198.13.46.22', port=3306, user='root', password='kamisama', db='spider'
        )
        self.cursor = self.connect.cursor()

    def close_spider(self, spider):
        self.cursor.close()
        self.connect.close()
        self.fp.close()
        print("爬虫结束")

    def log_wrong_url(self, url, e):
        self.fp.write(url)
        self.fp.write(':' + str(e))
        self.fp.write('\n')

    def process_item(self, item, spider):
        clean_data(item)
        if item.__class__.__name__ == "NovelItem":
            novel_sql = '''insert into novel(id,title,author,novel_type,intro)
            values('{}','{}','{}','{}','{}')'''.format(
                item['novel_id'],
                item['novel_title'],
                item['novel_author'],
                item['novel_type'],
                item['novel_intro'],)
            try:
                self.cursor.execute(novel_sql)
                self.connect.commit()
            except Exception as e:
                self.log_wrong_url(item['url'], e)
                print(e)
                print(item['url'])
                print(novel_sql)
                self.connect.rollback()

        else:
            chapter_sql = '''
            insert into chapter(title, novel_id, content_id)
            values(
            '{}','{}','{}'
            )
            '''.format(
                item['chapter_title'],
                item['novel_id'],
                item['chapter_id'],
            )
            # 插入chapter表
            try:
                self.cursor.execute(chapter_sql)
                self.connect.commit()
                #  print(item)
            except Exception as e:
                print(e)
                print(item['url'])
                #  print(chapter_sql)
                self.log_wrong_url(item['url'], e)
                self.connect.rollback()
            content_sql = '''
            insert into content(id,content)
            values(
            '{}','{}'
            )
            '''.format(item['chapter_id'], item['chapter_content'])
            try:
                self.cursor.execute(content_sql)
                self.connect.commit()
            except Exception as e:
                self.log_wrong_url(item['url'], e)
                print(e)
                print(item['url'])
                print(content_sql)
                self.connect.rollback()
        return item
