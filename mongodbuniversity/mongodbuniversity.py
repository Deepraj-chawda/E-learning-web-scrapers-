import scrapy

import pandas as pd
from scrapy.crawler import CrawlerProcess


all_data = pd.DataFrame(dict())

class Spider(scrapy.Spider):
    name = "mongodb"

    def start_requests(self):
        url = 'https://university.mongodb.com/courses/catalog?'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        links = response.css('section.css-hym75y a::attr(href)').extract()
        links = ['https://university.mongodb.com'+l for l in links]
        for link in links:
            yield scrapy.Request(url=link,callback=self.getdata)

    def getdata(self,response):
        global all_data
        data = dict()
        data['title'] = response.css('h1.css-wpx0a7::text').extract_first()

        data['about'] = response.css('p.css-nw3lhu::text').extract_first()

        data['video_link'] = response.css('video source::attr(src)').extract_first()

        data['course-requirements'] = str(response.css('div#course-about-requirements p::text').extract())

        data["What You'll Learn"] = str(response.css('div.css-i3pbo p::text').extract())

        data['PREREQUISITES'] = str(response.css('div.css-1me3qen *::text').extract())

        data['Course Details'] = str(response.css('div.css-j5ahe5 p::text').extract())

        data['Course Agenda'] = str(response.css('div.css-h1lou9 p::text').extract())

        data['instructor-name'] = response.css('p.e1al7i7h4::text').extract()[-3]

        data['question-answers'] = str(response.css('div.css-182pr9h p::text').extract())

        data['completion'] = response.css('div.css-1989ovb p::text').extract_first()

        data = pd.DataFrame(data, index=[0])
        all_data = pd.concat([all_data, data], ignore_index=True)


if __name__ == "__main__":
    process = CrawlerProcess()

    process.crawl(Spider)

    process.start()
    all_data.to_csv('mongodb_course_data.csv')
    print("mongodb_course_data.csv is stored")
