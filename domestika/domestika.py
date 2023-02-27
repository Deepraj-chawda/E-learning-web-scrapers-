import scrapy
import requests
import pandas as pd
from scrapy.crawler import CrawlerProcess

from bs4 import BeautifulSoup
from os.path import exists

all_data = pd.DataFrame(dict())

class SkillshareSpider(scrapy.Spider):
    name = "skillshare"

    def start_requests(self):
        file_link = exists('domestika_links.csv')
        print(file_link)
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
        if file_link:

            d = pd.read_csv('domestika_links.csv', index_col=0)
            urls = list(d['links'])
        else:
           print('run domestika_links.py')

        for url in urls[:20]:
            yield scrapy.Request(url=url, callback=self.parse,headers=headers)

    def parse(self, response):
        global all_data
        data = dict()
        # getting title
        title = response.css('h1.course-header-new__title a::text').extract_first()
        data['title'] = title
        cob = response.css('a.js-teacher-popover-link::text').extract_first()
        data['courseBY'] = cob
        price = response.css('span.m-price--code::text').extract_first()
        data['price'] = price

        li = response.css('li.toc-summary__item div.media-body::text').extract()
        li = [l for l in li if l!='\n']
        data['What-will-you-learn'] = str(li)

        l = response.css('li.gap-xs')

        data['positive-reviews'] = l[0].css('span::text').extract_first()
        data['student/alumnos'] = l[1].css('span::text').extract_first()
        data['lessons'] = l[2].css('span::text').extract_first()
        data['additional-resources'] = l[3].css('span::text').extract_first()
        data['online'] = l[4].css('span::text').extract_first()
        data['Available'] = l[5].css('span::text').extract_first()
        data['audio'] = l[6].css('span::text').extract_first()
        data['language'] = str(''.join(l[7].css('span::text').extract()))
        data['level'] = l[8].css('span::text').extract()[1]
        data['access'] = l[9].css('span::text').extract_first()

        des = response.css('div.course-landing__description *::text').extract()
        data['description'] = ''.join(des)

        con = response.css('li.toc-new__item')
        lesson= {}
        for c in con:
            title = c.css('div.row h4::text').extract_first().strip()
            ls = c.css('div.row div.toc-new__lesson-title::text').extract()
            lesson[title]=ls
        data['lesson_content'] = str(lesson)

        data = pd.DataFrame(data, index=[0])
        all_data = pd.concat([all_data, data], ignore_index=True)


if __name__ == "__main__":
    process = CrawlerProcess()

    process.crawl(SkillshareSpider)

    process.start()
    all_data.to_csv('domestika_course_data.csv')
    print("domestika_course_data.csv is stored")
