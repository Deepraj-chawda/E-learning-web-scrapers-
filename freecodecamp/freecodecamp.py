import scrapy
import pandas as pd
import requests
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup
from os.path import exists

all_data = pd.DataFrame(dict())

class Spider(scrapy.Spider):
    name = "freecodecamp"

    def start_requests(self):
        file_link = exists('freecodecamp_links.csv')
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
        if file_link:

            d = pd.read_csv('freecodecamp_links.csv')
            urls = list(d.loc[:,'links'])
        else:
            re = requests.get('https://www.freecodecamp.org/news/sitemap-posts.xml')
            s = BeautifulSoup(re.content, ['xml'])
            links = s.find_all('loc')

            urls = [l.text for l in links if
                     l.text.startswith('https://www.freecodecamp.org/news/') and 'images' not in l.text]
            links = pd.DataFrame(urls, columns=['links'])
            links.to_csv('freecodecamp_links.csv')

            print('scrapped all links and save it in freecodecamp_links.csv')

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse,headers=headers)

    def parse(self, response):
        global all_data
        data = dict()
        # getting title

        data['title'] = response.css('h1.post-full-title::text').extract_first()

        data['date'] = response.css('time.post-full-meta-date::text').extract_first().strip()

        tag = response.css('section.post-full-meta a::text').extract_first()
        if tag:
            data['tag'] = tag.strip()

        author = response.css('span.author-card-name a::text').extract_first()
        if author:
            data['author'] = author.strip()

            data['author_profile_link'] = 'https://www.freecodecamp.org' + response.css('span.author-card-name a::attr(href)').extract_first()

            data['author_Bio'] = response.css('section.author-card-content p::text').extract_first()

        data['post_image_link'] = response.css('figure.post-full-image img::attr(src)').extract_first()


        data['post-content'] = str(response.css('section.post-content *::text').extract())

        data = pd.DataFrame(data, index=[0])
        all_data = pd.concat([all_data, data], ignore_index=True)


if __name__ == "__main__":
    process = CrawlerProcess()

    process.crawl(Spider)

    process.start()
    all_data.to_csv('freecodecamp_course_data.csv')
    print("freecodecamp_course_data.csv is stored")
