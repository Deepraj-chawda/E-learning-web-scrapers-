import requests
from bs4 import BeautifulSoup
import pandas as pd
import undetected_chromedriver.v2 as chrome_driver
import warnings
import time
from os.path import exists
warnings.filterwarnings("ignore")


def scrap(driver):
    print('start..')
    file_link = exists('dataquest_links.csv')

    if file_link:

        d = pd.read_csv('dataquest_links.csv')
        urls = list(d.loc[:, 'links'])
    else:

        # get requests on page
        driver.get('https://www.dataquest.io/data-science-courses/individual-courses/')
        soup = BeautifulSoup(driver.page_source)

        urls = soup.find_all('a',attrs={"class":'stretched-link'})
        urls = ["https://www.dataquest.io" + a['href'] for a in urls]

        links = pd.DataFrame(urls, columns=['links'])
        links.drop_duplicates(subset="links", inplace=True)
        links.to_csv('dataquest_links.csv')
        print(f'scrapped all links and save it in dataquest_links.csv')

    all_data = pd.DataFrame(dict())
    count = 1
    for url in urls:
        try:
            driver.get(url)
            s = BeautifulSoup(driver.page_source)
            data = dict()

            data['course-name'] = s.find('h1', attrs={"id": "course-name"}).text
            
            data['course-description'] = s.find('p', attrs={"id": "course-description"}).text

            inst = s.find('div', attrs={"class": "banner-right mt-lg-0 mt-md-0 mt-5"})
            if inst:
                data['teacher_name'] = inst.h4.text
                data['teacher_bio'] = inst.p.text
                data['teacher_profession'] = inst.span.text
                data['teacher_img'] = inst.img['src']

            div = s.find('div', attrs={'class': 'text-inner pt-3'})
            if div:
                rat, review = div.p.text.split('(')
                data['ratings'] = rat
                data['reviews'] = review[:-1]

            learn = div.find('span', attrs={"id": 'course-signups'})
            if learn:
                data['learners'] = learn.text

            hour = div.find('li',attrs={'id':'hours'})
            if hour:
                data['hours'] = hour.text

            lesson = div.find('li',attrs={'id':'lesson-count'})
            if lesson:
                data['lessons'] = lesson.text

            project = div.find('li',attrs={'id':'project-count'})
            if project:
                data['project'] = project.text

            over = s.find('section', attrs={'id': 'overview-sec'}).find('div', attrs={"class": "text-box"})
            if over:
                data['Course overview'] = over.text.strip()

            skill = s.find('section', attrs={'id': 'key-skills-sec'}).find_all('li')
            if skill:
                data['Key skills'] = str([sk.text for sk in skill])

            les_data = {}
            out = s.find('section', attrs={'id': 'course-outline-sec'}).find_all('li', attrs={'class': 'mb-5'})
            for les in out:
                les_data[les.h4.text] = les.ul.text
            data['Course outline'] = str(les_data)

            proj = s.find('section', attrs={'id': "projects-sec"}).find('div', attrs={"class": "project-box mt-4 p-4"})
            if proj:
                data['project_title'] = proj.h4.text
                data['about_project'] = proj.p.text
                data['project_link'] = proj.a['href']

            data = pd.DataFrame(data, index=[0])
            all_data = pd.concat([all_data, data], ignore_index=True)
        except :
            #print(f'unable to scrap link {url}')
            continue
        finally:
            print(count)
            count += 1

    all_data.to_csv('dataquest_course_data.csv')
    print("dataquest_course_data.csv is stored")


if __name__ == "__main__":
    options = chrome_driver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.headless = True
    driver = chrome_driver.Chrome(options=options)
    scrap(driver)
