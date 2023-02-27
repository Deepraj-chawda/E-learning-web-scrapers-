import scrapy
import requests
import pandas as pd
from scrapy.crawler import CrawlerProcess

from bs4 import BeautifulSoup
from os.path import exists

all_data = pd.DataFrame(dict())

class SkillshareSpider(scrapy.Spider):
    name = "skillshare"

    def start_requests(self):
        file_link = exists('Final Course List (July - Dec 2022).xlsx')
        print(file_link)
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
        if file_link:

            d = pd.read_excel('Final Course List (July - Dec 2022).xlsx')
            urls = list(d.loc[:,"Click here to join the course"])
        else:
           print('Final Course List (July - Dec 2022).xlsx file not found')

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse,headers=headers)

    def parse(self, response):
        global all_data
        data = dict()
        # getting title
        data['title'] = response.css('h1.courseTitle::text').extract_first()
        data['instructorName'] = response.css('div.instructorName::text').extract_first().strip()
        data['learnerEnrolled'] = response.css('div.learnerEnrolled::text').extract_first()
        l = response.css('div.previewContent *::text').extract()
        data['about_the_course'] = l[1]
        name =response.css('h3.profileName::text').extract()
        data['instructor_names'] = str(name)
        soup = BeautifulSoup(response.text)
        boi = soup.find_all('div',attrs={'class':'col-md-9 col-sm-9 col-xs-12'})
        data['instructor_boi'] = str([b.text for b in boi])
        course = soup.find_all('div',attrs={"class":'previewContent marginTop20'})

        try:
            data['Course-certificate'] = course[3].text
        except:
            pass
        data['course'] = str(course[0].text)
        data['Books-and-references'] = str(course[1].text)


        data = pd.DataFrame(data, index=[0])
        all_data = pd.concat([all_data, data], ignore_index=True)


if __name__ == "__main__":
    process = CrawlerProcess()

    process.crawl(SkillshareSpider)

    process.start()
    all_data.to_csv('nptel_course_data.csv')
    print("nptel_course_data.csv is stored")
