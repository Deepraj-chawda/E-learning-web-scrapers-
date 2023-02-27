import scrapy
import requests
import pandas as pd
from scrapy.crawler import CrawlerProcess

from bs4 import BeautifulSoup
from os.path import exists

all_data = pd.DataFrame(dict())

class Spider(scrapy.Spider):
    name = "opensap"

    def start_requests(self):
        file_link = exists('opensap_links.csv')
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
        if file_link:

            d = pd.read_csv('opensap_links.csv')
            urls = list(d.loc[:,'links'])
        else:
           print('opensap_links.csv file not found')

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse,headers=headers)

    def parse(self, response):
        global all_data
        data = dict()
        # getting title
        data['title'] = response.css('div.header-title::text').extract_first()
        data['Instructor'] = response.css('div.header-subtitle::text').extract_first()
        teachers = response.css('div.teacher-text')
        td = []
        profiles = []
        for t in teachers:
            td.append(t.css('p::text').extract_first())
            profiles.append(t.css('a::attr(href)').extract())

        data['Instructor_about'] = str(td)
        data['Instructor_profiles'] = str(profiles)

        info = response.css('span.shortinfo span.ml5::text').extract()
        for i in info:
            if 'Language' in i:
                data['Language'] = i
            elif 'Subtitles' in i:
                data['Subtitles'] = i
            else:
                data['date'] = i

        data['course-information'] = str(response.css('div.course-information *::text').extract())

        req = response.css('ul.certificate-requirements li')
        req_data = []
        for r in req:
            req_data.append(''.join(r.css('*::text').extract()))
        data['certificate-requirements'] = str(req_data)

        con = response.css('ul.list-unstyled li')

        con_data = []
        for c in con:
            con_data.append(''.join(c.css('*::text').extract()))

        data['Course contents'] = str(con_data)

        learner = response.css('div.enrollment-statistics__count::text').extract()
        if learner:
            data['current_learners'] = learner[0]
            data['end_learners'] = learner[1]
            data['start_learners'] = learner[2]


        data = pd.DataFrame(data, index=[0])
        all_data = pd.concat([all_data, data], ignore_index=True)


if __name__ == "__main__":
    process = CrawlerProcess()

    process.crawl(Spider)

    process.start()
    all_data.to_csv('opensap_course_data.csv')
    print("opensap_course_data.csv is stored")
