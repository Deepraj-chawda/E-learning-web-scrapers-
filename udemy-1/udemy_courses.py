import undetected_chromedriver.v2 as chrome_driver
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
from bs4 import BeautifulSoup
from time import sleep
from os.path import exists


class UdemyScrap:
    def __init__(self):
        self.options = chrome_driver.ChromeOptions()
        self.options.add_argument("--start-maximized")
        #self.options.headless = True


    def scrap_courses(self):
        print('getting courses links ...')
        file_link = exists('courses_links_udemy.csv')
        if file_link:
            d = pd.read_csv('courses_links_udemy.csv', index_col=0)
            all_links = list(d['links'])
        else:
            print('Run udemy_links.py first')
        print('course links scrapped')
        try:
            file_exists = exists('udemy_value.txt')
            if file_exists:
                with open('udemy_value.txt', 'r') as file:
                    value = int(file.read())

                    count = value + 1
                all_data = pd.read_csv('udemy_course_data.csv', index_col=0)

            else:
                value = 0
                all_data = pd.DataFrame(dict())
                count = 1
            if value == len(all_links):
                print('Already Scrapped all links....')
                input_val = int(input('\nEnter 1 for scrapping again : '))
                if input_val == 1:
                    value = 0
                    count = 1
                    all_data = pd.DataFrame(dict())

            self.driver = chrome_driver.Chrome(options=self.options)

            for link in all_links[value:]:
                data = dict()
                self.driver.get(link)
                sleep(2)
                try:
                    # name
                    data['name'] = self.driver.find_element_by_class_name('udlite-heading-xl').text
                    # text-under-name
                    data['text-under-name'] = self.driver.find_element_by_class_name('clp-lead__headline').text
                    # rating-number
                    data['rating-number'] = self.driver.find_element_by_class_name('star-rating--rating-number--2o8YM').text
                    # number-of-ratings
                    data['number-of-ratings'] = \
                    self.driver.find_element_by_class_name('styles--rating-wrapper--5a0Tr').find_elements_by_tag_name(
                        'span')[-1].text[1:-1].rstrip(' ratings')
                    # number-of-students
                    data['number-of-students'] = self.driver.find_element_by_class_name('enrollment').text.rstrip(
                        ' students')
                except:
                    print(f'link {count} is not found')
                    count += 1
                    continue
                # Instructor-name
                names = self.driver.find_element_by_class_name('instructor-links--names--7UPZj').find_elements_by_tag_name('a')
                for i in range(len(names)):
                    data[f'Instructor-name-{i+1}'] = names[i].text
                # what you will learn
                try:
                    points = self.driver.find_element_by_class_name('what-you-will-learn--content-spacing--3btHJ').find_elements_by_tag_name('li')
                    data['what-you-learn'] = str([p.text for p in points])

                except:
                    pass
                # price
                price = self.driver.find_element_by_class_name('price-text--price-part--2npPm').text.split()[-1]
                data['price'] = price

                soup = BeautifulSoup(self.driver.page_source)
                if price == 'Free':
                    # no-hours-demand-video
                    dv = self.driver.find_element_by_class_name(
                        'course-content-length--course-content-length--1E1Pe').text.rstrip('of on-demand video')
                    data['no-hours-demand-video'] = dv
                else:

                    div = soup.find('div', attrs={'class': 'incentives--incentives-container--CUQ8q'})
                    li = div.find_all('li')
                    for i in li:
                        text = i.text
                        # no-hours-demand-video
                        if text.endswith('on-demand video'):
                            data['no-hours-demand-video'] = text.split()[0]
                        #number-of-articles
                        elif text.endswith('article') or text.endswith('articles'):
                            data['number-of-articles'] = text.split()[0]
                        # downloadable-resources
                        elif 'downloadable' in text:
                            data['downloadable-resources'] = text.split()[0]
                        #access
                        elif text.endswith('access'):
                            data['access'] = text.split()[0]

                # requirements
                req = soup.find_all('div', attrs={'class': "component-margin"})[1].text
                if 'Requirements' in req:
                    data['requirements'] = req.replace('Requirements', '')

                # Description
                des = soup.find('div', attrs={'class': "udlite-text-sm component-margin styles--description--3y4KY"})
                des.find_all('p')
                description = ''
                for i in des:
                    description += i.text.replace('\t', '')
                data['description'] = description.strip('Description ')

                # Who this course is for:
                wh = des.find_all('li')
                whos = ''
                for i in wh:
                    whos += i.text + '\n'
                if whos:
                    data['Who-is-this-course-for'] = whos

                # Instructor-name
                if price == "Free":
                    self.driver.find_element_by_class_name('carousel--container--37Pr-').find_elements_by_tag_name('button')[3].click()
                instr = self.driver.find_elements_by_class_name('instructor--instructor--1wSOF')

                for i in range(len(instr)):
                    instructors = instr[i].find_element_by_class_name('instructor--instructor__image-and-stats--1IqE7')
                    name = instr[i].find_element_by_class_name('instructor--instructor__title--34ItB').text
                    data[f'Instructor-name-{i + 1}'] = name
                    data_ins = instructors.text.split('\n')
                    for d in data_ins:

                        # instructor-rating
                        if 'Instructor Rating' in d:
                            data[f'instructor-rating-{i + 1}'] = d.rstrip('Instructor Rating')
                        # instructor-reviews
                        elif 'Reviews' in d:
                            data[f'instructor-reviews-{i + 1}'] = d.rstrip('Reviews')
                        # instructor-students
                        elif 'Students' in d:
                            data[f'instructor-students-{i + 1}'] = d.rstrip('Students')
                        # instructor-course
                        elif 'Courses' in d:
                            data[f'instructor-students-{i + 1}'] = d.rstrip('Courses')
                #course-content
                if price == "Free":
                    self.driver.find_element_by_class_name('carousel--container--37Pr-').find_elements_by_tag_name('button')[1].click()
                try:

                    self.driver.find_element_by_class_name(
                        'curriculum--curriculum-sub-header--3_-6E').find_element_by_tag_name('button').click()
                except:
                    pass
                soup = BeautifulSoup(self.driver.page_source)
                lessons = soup.find_all('div', attrs={'class': 'section--panel--1tqxC panel--panel--3uDOH'})
                lessons_data = []
                for lesson in lessons:
                    l_d = dict()
                    title = lesson.find('span', attrs={'class': "udlite-accordion-panel-title"}).span.text

                    points = lesson.find_all('li')
                    points_data = []
                    for p in points:
                        point = p.find('div', attrs={'class': "udlite-block-list-item-content"}).span.text
                        points_data.append(point)
                    l_d[title] = points_data
                    lessons_data.append(l_d)
                data['course-content'] = str(lessons_data)

                #reviews
                if price == "Free":
                    self.driver.find_element_by_class_name('carousel--container--37Pr-').find_elements_by_tag_name('button')[2].click()
                reviews = self.driver.find_elements_by_class_name('reviews-section--review-container--3F3NE')
                names = []
                rev_texts = []
                ratings = []
                for review in reviews:
                    name = review.find_element_by_class_name('individual-review--individual-review__name--3slEE').text
                    rev_text = review.find_element_by_class_name(
                        'individual-review--individual-review__comment--2o94n').text
                    rate = review.find_element_by_class_name('star-rating--large--25176').text.split()[1]
                    names.append(name)
                    rev_texts.append(rev_text)
                    ratings.append(rate)
                # review-name
                if names:
                    data['review-names'] = str(names)
                # review-description
                if rev_texts:
                    data['review-descriptions'] = str(rev_texts)
                # review-ratings
                if ratings:
                    data['review-ratings'] = str(ratings)

                data = pd.DataFrame(data,index=[0])
                all_data = pd.concat([all_data, data], ignore_index=True)
                print(f'link {count} scrapped')
                count += 1

            all_data.to_csv('udemy_course_data.csv')
            print('udemy_course_data.csv is stored' )
            return all_data

        except Exception as e:
            print(e)
            all_data.to_csv('udemy_course_data.csv')
            print(f'data saved upto link {count - 1} in udemy_course_data.csv ')

        finally:
            with open('udemy_value.txt', 'w') as file:
                file.write(str(count - 1))
            all_data.to_csv('udemy_course_data.csv')
            return all_data



if __name__ == "__main__":
    scrap = UdemyScrap()
    data = scrap.scrap_courses()
