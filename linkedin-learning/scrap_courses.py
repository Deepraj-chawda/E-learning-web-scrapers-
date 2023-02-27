import undetected_chromedriver.v2 as chrome_driver
import pandas as pd
from time import sleep
import warnings
warnings.filterwarnings("ignore")


class ScrapCourse:
    def __init__(self):
        #reading csv file
        self.csv_file = pd.read_csv('LinkedInLearningALC_GOOGLE.csv')
        # start webdriver
        options = chrome_driver.ChromeOptions()
        options.add_argument("--start-maximized");
        options.headless = True
        self.driver = chrome_driver.Chrome(options=options)
        

    def scrap_link(self,link,driver):
        # for storing data
        data = dict()
        print('start scrapping........')
        # get request on page
        driver.get(link)   
        # getting title
        data['title'] = driver.find_element_by_class_name('top-card-layout__title').text

        headline = driver.find_elements_by_class_name('top-card__headline-row')[1]
        headline_data = headline.find_elements_by_tag_name('span')
        # getting intermediate text
        data['text_intermediate'] = headline_data[1].text.lstrip('Skill level: ')
        # getting time
        data['time'] = headline_data[0].text.lstrip('Duration: ')
        #getting released
        data['released'] = headline_data[2].text.lstrip('Released: ') 
        try:
            #getting rating-number
            data['rating-number'] = driver.find_element_by_class_name('ratings-summary__rating-average').text
        except:
            pass
        # getting whats-included
        what_included_points = driver.find_element_by_class_name('aside-section-container__content')
        all_points = what_included_points.find_elements_by_class_name('subscription-value-props-aside-section__list-item')
        points = []
        for point in all_points:
             points.append(point.find_elements_by_tag_name('span')[1].text) 
        data['whats-included'] = ','.join(points)

        #getting course-description
        data['course-description'] = driver.find_element_by_class_name('course-details__description').text.rstrip('\nShow more')

        #getting skills-covered
        data['skills-covered'] = driver.find_element_by_class_name('course-skills__skill-list-item').text

        #getting instructor
        data['instructor'] = driver.find_element_by_class_name('base-main-card__title').text
    
        # click on syllabus
        for i in range(3):
            buttons = driver.find_element_by_class_name('table-of-contents__list').find_elements_by_class_name('show-more-less')
            for b in buttons:
                try:
                    b.find_element_by_tag_name('button').click()
                    sleep(1)
                except:
                    continue
        try:
            button[0].find_element_by_tag_name('button').click()
        except:
            pass
        
        lessons = driver.find_elements_by_class_name('toc-section')
        #getting from all lessons
        for i in range(len(lessons)):
            titles = lessons[i].find_elements_by_class_name('toc-item')
            lesson = [title.find_element_by_class_name('table-of-contents__item-title').text for title in titles]
            data[f'what-you-will-learn-lesson-{i+1}'] = ','.join(lesson)

        data = pd.DataFrame(data,index=[0])
        return data

    def start(self):
        all_data = pd.DataFrame(dict())
        for i in range(len(self.csv_file)):
            link = self.csv_file.loc[i,'link']
            data = self.scrap_link(link,self.driver)
            
            all_data = pd.concat([all_data,data],ignore_index=True)
            print(f'link {i+1} scrapped')

        all_data.to_csv('data.csv')
        print("data.csv is stored")
        return all_data

if __name__ == '__main__':
    
    scrape_courses = ScrapCourse()
    data = scrape_courses.start()
    
