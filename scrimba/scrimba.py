import scrapy
import requests
import pandas as pd
from scrapy.crawler import CrawlerProcess

from bs4 import BeautifulSoup
from os.path import exists

all_data = pd.DataFrame(dict())

class Spider(scrapy.Spider):
    name = "scrimba"

    def start_requests(self):
        url = 'https://scrimba.com/allcourses'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        links = response.css('course-tile a::attr(href)').extract()
        links = ['https://scrimba.com'+l for l in links]

        for link in links:
            yield scrapy.Request(url=link,callback=self.getdata)

    def getdata(self,response):
        global all_data
        data = dict()
        title = response.css('h1.cq_bi::text').extract_first()
        if title:
            data['title'] = title

            data['teacher'] = response.css('h4.cq_bi strong::text').extract_first()

            data['level'] = response.css('span.cq_bi p::text').extract_first()

            data['about_course'] = response.css('p.cq-cb::text').extract_first()

            lessons = response.css('div.list')
            les_data = {}
            for l in lessons:
                mod = l.css('div.item div.title::text').extract_first()
                if mod:
                    les = l.css('a.item div.title::text').extract()
                    les_data[mod] = les

            data['lessons'] = str(les_data)

            learn = response.css('p.bullet::text').extract()

            data["You'll learn"] = str(learn)

            build = response.css('div.projects h5::text').extract()
            data["You'll build"] = str(build)

            pre = response.css('section.cq-dc p.cq-dg::text').extract()
            data['Prerequisites'] = str(pre)

            teach = response.css('p.cq-dq::text').extract_first()
            data['about_teacher'] = teach

            cou = response.css('div.cq-ej *::text').extract()
            data['Why this course rocks'] = str(cou)


        else:
            data['title'] = response.css('h1.ht_bk::text').extract_first()

            data['teacher'] = response.css('h4.ht_bk strong::text').extract_first()

            data['level'] = response.css('span.ht_bk p::text').extract_first()

            data['about_course'] = response.css('p.ht-cd::text').extract_first()

            teach = response.css('p.ht-dd::text').extract_first()
            data['about_teacher'] = teach

            cou = response.css('div.ht-di *::text').extract()
            data['Why this course rocks'] = str(cou)

        data = pd.DataFrame(data, index=[0])
        all_data = pd.concat([all_data, data], ignore_index=True)


if __name__ == "__main__":
    process = CrawlerProcess()

    process.crawl(Spider)

    process.start()
    all_data.to_csv('scrimba_course_data.csv')
    print("scrimba_course_data.csv is stored")
