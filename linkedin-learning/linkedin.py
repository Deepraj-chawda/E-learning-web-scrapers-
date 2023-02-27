<<<<<<< HEAD
import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
import undetected_chromedriver.v2 as chrome_driver
all_data = pd.DataFrame({})

class SpiderClassName(scrapy.Spider):
    name = "spider_name"


    def start_requests(self):
        # reading csv file
        self.csv_file = pd.read_csv('LinkedInLearningALC_GOOGLE.csv')

        for i in range(len(self.csv_file)):
            link = self.csv_file.loc[i, 'link']

            yield scrapy.Request(url=link, callback=self.parse)

    def parse(self, response):
        global all_data
        # for storing data
        data = dict()

        # getting title
        data['title'] = response.css('h1.top-card-layout__title::text').extract_first().strip()

        headline = response.css('div.top-card__headline-row')[1]
        headline_data = headline.css('span::text').extract()
        # getting intermediate text
        data['text_intermediate'] = headline_data[1].lstrip('Skill level: ')
        # getting time
        data['time'] = headline_data[0].lstrip('Duration: ')
        # getting released
        data['released'] = headline_data[2].lstrip('Released: ')

        # getting rating-number
        rat = response.css('span.ratings-summary__rating-average::text').extract_first()
        if rat:
            data['rating-number'] = rat

        # getting whats-included
        what_included_points = response.css('div.aside-section-container__content')[0]
        all_points = what_included_points.css(
            'li.subscription-value-props-aside-section__list-item')
        points = []
        for point in all_points:
            points.append(point.css('span::text').extract()[1])

        data['whats-included'] = ','.join(points)

        # getting course-description
        data['course-description'] = response.css('section.course-details__description div::text').extract_first().rstrip(
            '\nShow more').strip()

        # getting skills-covered
        data['skills-covered'] = response.css('li.course-skills__skill-list-item a::text').extract_first().strip()

        # getting instructor
        data['instructor'] = response.css('h3.base-main-card__title::text').extract_first().strip()

        lessons = response.css('li.toc-section')
        les_data = []
        # getting from all lessons
        for i in range(len(lessons)):
            titles = lessons[i].css('button.show-more-less__button::text').extract_first().strip()
            les_data.append(titles)
        data['syllabus'] = str(les_data)

        data = pd.DataFrame(data, index=[0])
        all_data = pd.concat([all_data, data], ignore_index=True)

if __name__ == "__main__":
    process = CrawlerProcess()

    process.crawl(SpiderClassName)

    process.start()
    all_data.to_csv('linkedin_course_data.csv')
    print("linkedin_course_data.csv is stored")


=======
import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
import undetected_chromedriver.v2 as chrome_driver
all_data = pd.DataFrame({})

class SpiderClassName(scrapy.Spider):
    name = "spider_name"


    def start_requests(self):
        # reading csv file
        self.csv_file = pd.read_csv('LinkedInLearningALC_GOOGLE.csv')

        for i in range(len(self.csv_file)):
            link = self.csv_file.loc[i, 'link']

            yield scrapy.Request(url=link, callback=self.parse)

    def parse(self, response):
        global all_data
        # for storing data
        data = dict()

        # getting title
        data['title'] = response.css('h1.top-card-layout__title::text').extract_first().strip()

        headline = response.css('div.top-card__headline-row')[1]
        headline_data = headline.css('span::text').extract()
        # getting intermediate text
        data['text_intermediate'] = headline_data[1].lstrip('Skill level: ')
        # getting time
        data['time'] = headline_data[0].lstrip('Duration: ')
        # getting released
        data['released'] = headline_data[2].lstrip('Released: ')

        # getting rating-number
        rat = response.css('span.ratings-summary__rating-average::text').extract_first()
        if rat:
            data['rating-number'] = rat

        # getting whats-included
        what_included_points = response.css('div.aside-section-container__content')[0]
        all_points = what_included_points.css(
            'li.subscription-value-props-aside-section__list-item')
        points = []
        for point in all_points:
            points.append(point.css('span::text').extract()[1])

        data['whats-included'] = ','.join(points)

        # getting course-description
        data['course-description'] = response.css('section.course-details__description div::text').extract_first().rstrip(
            '\nShow more').strip()

        # getting skills-covered
        data['skills-covered'] = response.css('li.course-skills__skill-list-item a::text').extract_first().strip()

        # getting instructor
        data['instructor'] = response.css('h3.base-main-card__title::text').extract_first().strip()

        lessons = response.css('li.toc-section')
        les_data = []
        # getting from all lessons
        for i in range(len(lessons)):
            titles = lessons[i].css('button.show-more-less__button::text').extract_first().strip()
            les_data.append(titles)
        data['syllabus'] = str(les_data)

        data = pd.DataFrame(data, index=[0])
        all_data = pd.concat([all_data, data], ignore_index=True)

if __name__ == "__main__":
    process = CrawlerProcess()

    process.crawl(SpiderClassName)

    process.start()
    all_data.to_csv('linkedin_course_data.csv')
    print("linkedin_course_data.csv is stored")


>>>>>>> 1a56a378bb158f6c986c6ce31d33ee570e3a17e5
