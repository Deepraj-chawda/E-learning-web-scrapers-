import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd

all_links = []

class SpiderClassName(scrapy.Spider):
    name = "spider_name"


    def start_requests(self):
        url = 'https://www.edureka.co/all-courses?page=1'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        links = response.css('a.page-link::attr(href)').extract()
        links = links[1:-1]

        for link in links:
            yield response.follow(url=link, callback=self.get_links)



    def get_links(self, response):
        links = response.css('a.ga-event-click::attr(href)').extract()
        all_links.extend(links)


if __name__ == "__main__":
    process = CrawlerProcess()

    process.crawl(SpiderClassName)

    process.start()
    print('scrapped all links ')
    print(len(all_links))
    all_links = pd.DataFrame(all_links, columns=['links'])
    all_links.to_csv('edureka_courses_links.csv')
