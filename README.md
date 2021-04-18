# biqugeSpider
> 爬取笔趣阁全站小说

## 数据库设计:

**小说表:** novel
| Field      | Type         | Null | Key | Default | 描述       |
|------------|--------------|------|-----|---------|------------|
| id         | char(11)     | NO   | PRI | NULL    | 小说表主键 |
| title      | varchar(128) | YES  |     | NULL    | 小说名     |
| intro      | varchar(500) | YES  |     | NULL    | 简介       |
| author     | varchar(20)  | YES  |     | NULL    | 作者       |
| novel_type | varchar(16)  | YES  |     | NULL    | 小说类型   |

**章节表:** chapter
| Field      | Type          | Null | Key | Default | extra          | 描述                   |
|------------|---------------|------|-----|---------|----------------|------------------------|
| id         | int           | NO   | PRI | NULL    | auto_increment | 章节id                 |
| title      | varchar(128)  | YES  |     | NULL    |                | 章节标题               |
| novel_id   | char(11)      | YES  |     | NULL    |                | 小说id(属于哪一部小说) |
| content_id | varchar(1024) | YES  |     | NULL    |                | 内容id(对应内容表id)   |

**内容表:** content
| Field   | Type | Null | Key | Default | 描述     |
|---------|------|------|-----|---------|----------|
| id      | int  | NO   | PRI | NULL    | 主键     |
| content | text | YES  |     | NULL    | 章节内容 |


## 数据爬取思路:

- 框架: 使用scrapy框架进行爬取(暂时只会这一个框架):
    - 使用CrawlSpder进行全站数据的爬取:
- 网站结构:
    - 从[排行榜单](https://www.biquge.info/paihangbang_allvisit/1.html)的页面可以检索到网站的全部小说数据:
        - 根据第一页提取所有分页的链接获取响应
        - 根据分页中的小说列表提取所有小说详情页的链接获取响应
        - 从详情页中提取所有章节的链接获取响应,提取小说表主键(id)、简介(intro)、作者(author)、小说名(title)和小说类型(novel_type),也就是小说表的全部内容
        - 从每一个章节的响应页面可以获取需要的 章节标题(title),小说id(novel_id)，内容id(content_id)和章节内容，这些数据分别存入两个表

## 编程思路:

- 创建爬虫项目:
    - `scrapy startproject biqugePro`
- 新建爬虫:
    - `scrapy genspider -t crawl biquge`
- 编写爬虫:
    - CrawlSpider已经使用了默认的parse()数据解析函数，所以只有实现自己的数据解析函数。
    - CrawlSpider根据LinkExtractor和Rule进行数据提取和请求发送
    - 需要编写三个链接提取器分别用来获取全部分页，全部详情页和全部章节的数据
- 反爬措施:
    - 编辑`setting.py`添加UA


## scrapy爬虫暂停和重启

### 记录爬取url的数据指纹
`scrapy crawl spider -s JOBDIR=./jobs/001`

## 改为分布式:

分布式就是搭建分布式机群对同一组资源进行分布联合爬取

就是多个计算机同时爬取一个网站用来提高爬取速度.

scrapy 是不支持分布式的，因为scrapy的五大组件在多台机器上是没有任何关系的，就算在多个计算机上运行同一个爬虫程序，也只是同一个程序在不同地方同时运行，达不到提升爬取速度的作用。所以需要使用scrapy-redis组件。

使用redis组件能使scrapy的调度器和下载器在多个计算机之间共享,这样多个计算机的爬虫程序公用一个待爬取的url队列，每台计算机都爬取的是未爬取过的url，共用一个待下载的请求队列，所有下载的请求都是没有被下载过的，而且可以设置将所有机器下载的数据汇总到一台机器上.

### 下载scrapy-redis

`pip install scrapy-redis`

#### 修改爬虫文件:

```
from scrapy_redis.spiders import RedisCrawlSpider
# 将爬虫类改为继承RedisCrawlSpider
# 注释掉start_urls和allowed_domains
# 添加新属性
redis_key = 'biquge'  #作为可以被共享的调度器名称
```
#### 修改配置文件:

- 指定使用可以被共享的管道:
    - `ITEM_PIPELINES={'scrapy_redis.pipelines.RedisPipeline':400}``
- 指定调度器:
    - 使用scrapy-redis组件的调度器:
        - `SCHEDULER = "scrapy_redis.scheduler.Scheduler"`
    - 配置调度器是否持久化:
        - `SCHEDULER_PERSIST = True` 设置为持久化，爬虫结束后不会清空redis中请求队列和去重指纹的set，使其可以暂停和重启
    - 增加去重容器类的配置,使用redis的set集合来存储请求的指纹数据:
        - `DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"`
- 
- redis相关操作:
    - 配置redis的配置文件:
        - linux/macos:redis.conf
        - windows:redis.windows.conf
        - 打开配置文件，修改:
            - `# bind 127.0.0.1`
            - 关闭保护模式:`protected-mode no`
        - 综合配置文件开启redis服务:
            - `redis-server 配置文件`
        - 启动客户端:
            - `redis-cli`
- 执行工程:
    - `scrapy runspider ***.py`
- 向调度器的队列中加入起始url:
    - 调度器队列:redis客户端中:
        - `lpush *** start_url`
- 抓取到的数据存储在redis的ProName:items的数据结构中


**TODO**

- [o]  全站数据爬取
    - [X] 数据库:
        - [X]  数据库设计
        - [X]  数据库实现
    - [o] 爬虫代码:
        - [X]  spider:爬虫入口，数据解析，url提取
    - [ ] 搭建分布式
    
    
