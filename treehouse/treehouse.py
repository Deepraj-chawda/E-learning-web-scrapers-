import scrapy
import pandas as pd
from scrapy.crawler import CrawlerProcess

all_data = pd.DataFrame(dict())

class Spider(scrapy.Spider):
    name = "treehouse"

    def start_requests(self):
        url = 'https://teamtreehouse.com/library/type:course'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        links = response.css('a.card-box::attr(href)').extract()
        links = ['https://teamtreehouse.com'+l for l in links]
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
        for link in links:
            yield scrapy.Request(url=link,callback=self.get_data,headers=headers)

    def get_data(self,response):
        global all_data
        data = dict()

        data['title'] = response.css('h1::text').extract_first()

        data['text_under-title'] = response.css('h2.markdown-zone::text').extract_first().strip()

        data['syllabus-description'] = response.css('div#syllabus-description p::text').extract_first()

        data["What-you'll-learn"] = str(response.css('div#syllabus-description li::text').extract())

        teachers = response.css('div#syllabus-authors li')

        data['teachers-name'] = str(teachers.css('h4::text').extract())

        data['about-teacher'] = str(teachers.css('div.markdown-zone p::text').extract())

        data['teachers-twitter'] = str(teachers.css('div.markdown-zone a::attr(href)').extract())

        data['syllabus-skill-level'] = response.css('li#syllabus-skill-level span::text').extract_first()

        data = pd.DataFrame(data, index=[0])

        all_data = pd.concat([all_data, data], ignore_index=True)

if __name__ == "__main__":
    process = CrawlerProcess()

    process.crawl(Spider)

    process.start()

    all_data.to_csv('treehouse_course_data.csv')
    print("treehouse_course_data.csv is stored")
