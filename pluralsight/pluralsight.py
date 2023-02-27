import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
from os.path import exists
from links_scrap import scrap

all_data = pd.DataFrame(dict())


class SpiderClassName(scrapy.Spider):
    name = "spider_name"

    def start_requests(self):


        file_link = exists('pluralsight_links.csv')
        if file_link:
            d = pd.read_csv('pluralsight_links.csv', index_col=0)
            urls = list(d['links'])

        else:
            sitemap = 'https://www.pluralsight.com/sitemap.xml'
            specific = 'https://www.pluralsight.com/courses/'
            filename = 'pluralsight_links.csv'
            urls = list(scrap(sitemap,specific,filename)['links'])

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        global all_data
        data = dict()

        # title
        data['title'] = response.css('div#course-page-hero').css('h1::text').extract_first()
        # author
        author = response.css('span.course-authors a::text').extract_first()
        if author:
            data['author'] = author.lstrip('by ')

        # description
        data['course_description'] = response.css('div#course-page-hero p::text').extract_first()
        # What you'll learn
        data["What-you'll-learn"] = response.css('div.course-page-section')[0].css('p::text').extract_first()

        # course info
        info = response.css('div.course-content-right-container')[4].css('div.course-info-rows')
        infos = []
        for i in info:
            infos.append(''.join(i.css('div *::text').extract()).replace('\n',''))
        for inf in infos:
            if "Level" in inf:
                # Level
                data['level'] = inf.lstrip('Level\n')
            elif "Updated" in inf:
                # Updated
                data['updated'] = inf.lstrip('Updated\n')
            elif 'Duration' in inf:
                # Duration
                data['duration'] = inf.lstrip('Duration\n')
            elif 'Rating' in inf:
                gray_star = len(info.css('i.gray'))
                half_star = len(info.css('i.fa-star-half-o')) / 2

                star = 5 - gray_star - half_star
                data['rating'] = star


            # About the author
            about_au = response.css('div.author-item p::text').extract_first()
            if about_au:
                data['About-the-author'] = about_au

            lessons = response.css('div.toc-item')
            lesson_data = {}
            for l in lessons:
                title = l.css('div.toc-title::text').extract_first().strip()
                li = l.css('div.toc-content li a span::text').extract()
                lesson_data[title] = li
            data['table-of-content'] = str(lesson_data)

            data = pd.DataFrame(data, index=[0])
            all_data = pd.concat([all_data, data], ignore_index=True)


if __name__ == "__main__":

    process = CrawlerProcess()

    process.crawl(SpiderClassName)

    process.start()
    all_data.drop_duplicates(subset="title", inplace=True)
    all_data.reset_index(inplace=True, drop=True)
    all_data.to_csv('pluralsight_course_data.csv')
    print('pluralsight_course_data.csv is stored')
