import undetected_chromedriver.v2 as chrome_driver
import pandas as pd
import warnings
from os.path import exists
import requests
warnings.filterwarnings("ignore")
from bs4 import BeautifulSoup
from time import sleep


def scrap_links(driver):
    file_link = exists('skillshare_links.csv')
    # get sitemap
    if file_link:

        d = pd.read_csv('skillshare_links.csv', index_col=0)
        urls = list(d['links'])
    else:
        re = requests.get('https://www.skillshare.com/sitemap/classes/1')
        soup = BeautifulSoup(re.content, ['xml'])
        urls = soup.find_all('loc')
        urls = [l.text for l in urls]
        links = pd.DataFrame(urls, columns=['links'])
        links.to_csv('skillshare_links.csv')

    # return links
    return urls


def scrap_course(driver):
    print('scrapping links....')
    # get all links
    links = scrap_links(driver)
    print('links scrapped')
    try:
        file_exists = exists('skillshare_value.txt')
        if file_exists:
            with open('skillshare_value.txt', 'r') as file:
                value = int(file.read())

                count = value + 1
            all_data = pd.read_csv('skillshare_course_data.csv', index_col=0)

        else:
            value = 0
            all_data = pd.DataFrame(dict())
            count = 1
        if value == len(links):
            print('Already Scrapped all links....')
            input_val = int(input('\nEnter 1 for scrapping again : '))
            if input_val == 1:
                value = 0
                count = 1
                all_data = pd.DataFrame(dict())

        for link in links[value:]:
            data = dict()
            # get request on page
            driver.get(link)
            soup = BeautifulSoup(driver.page_source)
            # title
            title = soup.find('span', attrs={'class': "title"})
            if title:
                data['title'] = title.text.strip()
            else:
                print(f'{link} not found')
                count += 1
                continue

            # teacher
            teacher = soup.find('h2', attrs={'class': 'class-details-header-teacher'}).text.split(',')
            data['teacher-name'] = teacher[0].strip()
            data['teacher-qualification'] = ','.join(teacher[1:]).strip()

            tl, duration = soup.find('div', attrs={'class': 'lesson-count'}).text.strip().split('(')
            #lesson-duration
            data['lesson-duration'] = duration.strip(')')
            #total-lesson
            data['total-lesson'] = tl

            #lessons
            ls = soup.find('div', attrs={'class': 'playlist'})
            lessons = ls.find_all('h3', attrs={'class': 'session-item-title'})
            if lessons:
                lessons = [l.text.strip() for l in lessons]
                data['all-lessons'] = str(lessons)

            # level
            level = soup.find('div', attrs={'class': 'level-text'}).find('li', attrs={'class': 'active'})
            if level:
                data['level'] = level.text
            p = soup.find_all('p', attrs={'class': 'class-count number'})
            if p:
                # student
                data['student-number'] = p[0].text.strip()
                # project
                data['project'] = p[1].text.strip()

            # About This Class
            class_a = soup.find('div', attrs={'class': 'description-column'})
            if class_a:
                data['about-this-class'] = class_a.text

            # Meet Your Teacher
            mt = soup.find('div', attrs={'class': 'teacher-description rich-content-wrapper'})
            if mt:
                data['meet-your-teacher'] = mt.text

            # Related Skills
            rs = soup.find('div', attrs={'class': 'tags-section'})
            if rs:
                data['related-skills'] = rs.text.strip().lstrip('Related Skills')

            # Hands-on Class Project
            pro = soup.find('div', attrs={"id": "project-gallery"})
            if pro:
                data['hands-on-project'] = pro.text.strip().lstrip('Hands-on Class Project')

            # most-liked-text
            ratings = soup.find_all('li', attrs={'class': 'js-tag-template'})
            if ratings:
                data['most-liked-text'] = str([r.text.strip() for r in ratings])

            exp = soup.find('div', attrs={'class': 'tile expectations metric'})
            if exp:
                pert = exp.find_all('li')

                #exceeded-percentage
                data['exceeded-percentage'] = pert[0].text
                #yes-ppercentage
                data['yes-ppercentage'] = pert[1].text
                #somewhat-percentage
                data['somewhat-percentage'] = pert[2].text
                #not-really-percentage
                data['not-really-percentage'] = pert[3].text

            #transcripts-content
            transcript =  soup.find('div', attrs={'class': 'transcripts-content'})
            if transcript:
                data['transcripts-content'] = transcript.text

            data = pd.DataFrame(data, index=[0])
            all_data = pd.concat([all_data, data], ignore_index=True)
            print(f'scrapped link {count}')
            count += 1

        all_data.to_csv('skillshare_course_data.csv')
        print('skillshare_course_data.csv is stored')
        return all_data
    except Exception as e:
        print(e)
        all_data.to_csv('skillshare_course_data.csv')
        print(f'data saved upto link {count - 1} in skillshare_course_data.csv ')

    finally:
        with open('skillshare_value.txt', 'w') as file:
            file.write(str(count - 1))
        all_data.to_csv('skillshare_course_data.csv')
        return all_data


if __name__ == "__main__":
    options = chrome_driver.ChromeOptions()
    options.add_argument("--start-maximized");
    #PROXY = "11.456.448.110:800"
    #options.add_argument('--proxy-server=%s' % PROXY)
    #options.headless = True
    driver = chrome_driver.Chrome(options=options)
    data = scrap_course(driver)
