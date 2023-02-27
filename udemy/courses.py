import undetected_chromedriver.v2 as chrome_driver
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
from bs4 import BeautifulSoup


class ScrapCourses_link:
    def __init__(self):
        options = chrome_driver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.headless = True
        self.driver = chrome_driver.Chrome(options=options)

    def get_course__topic_sitemap(self):
        self.driver.get('https://www.udemy.com/sitemap.xml')
        soup = BeautifulSoup(self.driver.page_source, ['xml'])
        links = soup.find_all('loc')
        courses = [link.text for link in links[1:2026]]
        topics = [link.text for link in links[-39:]]

        return courses, topics

    def get_courses_link(self):
        courses, topics = self.get_course__topic_sitemap()
        all_course_links = []
        for course in courses:
            self.driver.get(course)
            soup = BeautifulSoup(self.driver.page_source, ['xml'])
            links = soup.find_all('loc')
            course_links = [link.text for link in links]
            all_course_links.extend(course_links)
            print('scrapping links..')

        all_links = pd.DataFrame(all_course_links ,columns=['links'])
        all_links.to_csv('courses_links.csv')
        self.driver.close()
        return all_course_links
