import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd

all_links = []

class Center(scrapy.Spider):
    name = "center"

    def start_requests(self):

        link = 'https://www.classcentral.com/provider/aws-skill-builder?page={}'

        for i in range(1,204):

            yield scrapy.Request(url=link.format(i), callback=self.parse)

    def parse(self, response):
        global all_links
        a = response.css('a.course-name::attr(href)').extract()
        a = ['https://www.classcentral.com'+i for i in a ]
        all_links.extend(a)
        print('srapping')
        print(len(a))


if __name__ == "__main__":
    process = CrawlerProcess()

    process.crawl(Center)

    process.start()
    all_links = pd.DataFrame(all_links, columns=['links'])
    all_links.drop_duplicates(subset="links", inplace=True)
    all_links.to_csv('classcenter_links.csv')
    print('Data saved in classcenter_links.csv')