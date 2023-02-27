import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
all_links = []

class Future_learn(scrapy.Spider):
    name = "future_learn"

    def start_requests(self):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
        url = 'https://www.futurelearn.com/courses'
        yield scrapy.Request(url=url, callback=self.parse, headers=headers)

    def parse(self, response):
        link_no = response.css('li.pagination-module_item__3XB-l a::text').extract()[-1]

        print(link_no)
        for i in range(1,int(link_no)+1):
            yield scrapy.Request(url=f'https://www.futurelearn.com/courses?&page={i}',callback=self.get_link)

    def get_link(self,response):
        link = response.css('div.m-filter__content').css('div.m-card div.Body-wrapper_1NnVP a.link-wrapper_1GLAu::attr(href)').extract()
        link = ['https://www.futurelearn.com'+l for l in link]
        print(len(link))
        all_links.extend(link)


if __name__ == "__main__":
    process = CrawlerProcess()

    process.crawl(Future_learn)

    process.start()
    links = pd.DataFrame(all_links, columns=['links'])
    links.to_csv('futurelearn_links.csv')
    print('scrapped all links and save it in futurelearn_links.csv')
    