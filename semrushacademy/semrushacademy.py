import scrapy

import pandas as pd
from scrapy.crawler import CrawlerProcess


all_data = pd.DataFrame(dict())

class Spider(scrapy.Spider):
    name = "semrush"

    def start_requests(self):

        yield scrapy.Request(url="https://www.semrush.com/academy/courses/?spec=ALL&lang=en-US", callback=self.parse)

    def parse(self, response):

        links = response.css('div.acd-card a::attr(href)').extract()
        links = ['https://www.semrush.com'+l for l in links]
        print(len(links))
        print('links scrapped')

        for link in links:
            yield scrapy.Request(url=link,callback=self.getdata)

    def getdata(self,response):
        global all_data
        data = dict()
        data['title'] = response.css('h1.promo-title ::text').extract()[1]
        data['about'] = response.css('p.product-advert-text ::text').extract_first()
        des = response.css('div.description-item')

        data['lessons'] = des[0].css('h4::text').extract_first()
        data['lessons_text'] = des[0].css('p::text').extract_first()

        data['hours'] = des[1].css('h4::text').extract_first()
        data['hours_text'] = des[1].css('p::text').extract_first()

        data['price'] = des[2].css('h4::text').extract_first()
        data['price_text'] = des[2].css('p::text').extract_first()

        less_str = {}
        for d in des[3:]:
            tit = d.css('h4::text').extract_first()
            para = d.css('p::text').extract_first()
            less_str[tit] = para
        data['Lesson structure'] = str(less_str)

        data['Who is this course for'] = response.css('div.ac-p16::text').extract_first()

        data['About the author'] = response.css('div#5baa20c9779fb9afaac712ca p.ac-p16::text').extract_first()
        data['What to do after the course'] = str(response.css('div#5bab6ea54ae1caf591e0d9e0 div.right *::text').extract())

        data = pd.DataFrame(data, index=[0])
        all_data = pd.concat([all_data, data], ignore_index=True)

if __name__ == "__main__":
    process = CrawlerProcess()

    process.crawl(Spider)

    process.start()
    all_data.to_csv('semrushacademy_course_data.csv')
    print("semrushacademy_course_data.csv is stored")
