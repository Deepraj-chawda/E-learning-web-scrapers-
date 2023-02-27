import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
from os.path import exists

all_data = pd.DataFrame(dict())
class SpiderClassName(scrapy.Spider):
    name = "spider_name"

    def start_requests(self):

        file_link = exists('futurelearn_links.csv')
        if file_link:
            d = pd.read_csv('futurelearn_links.csv', index_col=0)
            urls = list(d['links'])
            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse)
        else:
            print('please run futurelearn_link_scrap.py first then run this file')

    def parse(self, response):
        global all_data
        data = dict()
        data['title'] = response.css('div.stack-module_item__1UYFV div h1::text').extract_first()
        text = response.css('div.PageHeader-introduction_C4C7_ p::text').extract_first()
        if text :
            data['text-under-name'] = text
        else:
            data['text-under-name'] = response.css('p.text-module_wrapper__FfvIV::text').extract_first()

        r = response.css('li.keyInfo-module_item__2GNi_ span.keyInfo-module_content__1K_85::text').extract()
        data['duration'] = r[0]
        data['no-of-hours'] = r[1]

        topic = response.css('section#section-topics li::text').extract()
        if topic:
            data['what-topics'] = str(topic)

        data['what-will-you-achieve'] = str(response.css('div.spacer-module_top-4__1o73p li div.listItemWithIcon-module_text__18TIF::text').extract())
        data['who-is-this-course-for'] = str(response.css('section#section-requirements p::text').extract())

        data['description'] = str(response.css('section#section-overview *::text').extract())
        data['course_university_image'] = response.css('section#section-creators img.image-module_image__1vzg2::attr(src)').extract_first()
        data['course_university'] = response.css('section#section-creators div.spotlight-content_2xV10 h2::text').extract_first()
        data['educators'] = str(response.css('div.educators-column_3xSeo h3 *::text').extract())

        data = pd.DataFrame(data, index=[0])
        all_data = pd.concat([all_data, data], ignore_index=True)

        #print(data)


if __name__ == "__main__":

    process = CrawlerProcess()

    process.crawl(SpiderClassName)

    process.start()
    all_data.to_csv('futurelearn_data.csv')
