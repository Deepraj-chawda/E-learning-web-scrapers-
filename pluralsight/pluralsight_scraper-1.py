import undetected_chromedriver.v2 as chrome_driver
import pandas as pd
import warnings
from os.path import exists

warnings.filterwarnings("ignore")
from bs4 import BeautifulSoup
from time import sleep


def scrap_links(driver):
    # get sitemap
    driver.get('https://www.pluralsight.com/sitemap.xml')
    # get all course links
    soup = BeautifulSoup(driver.page_source, ['xml'])
    links = soup.find_all('loc')
    links = [l.text for l in links if l.text.startswith('https://www.pluralsight.com/courses/')]
    # return links
    return links


def scrap_course(driver):
    print('scrapping links....')
    # get all links
    links = scrap_links(driver)
    print('links scrapped')
    try:
        file_exists = exists('plural_value.txt')
        if file_exists:
            with open('plural_value.txt', 'r') as file:
                value = int(file.read())

                count = value + 1
            all_data = pd.read_csv('pluralsight_course_data.csv', index_col=0)

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

            # title
            data['title'] = driver.find_element_by_id('course-page-hero').find_element_by_tag_name('h1').text
            # author
            try:
                data['author'] = driver.find_element_by_class_name('course-authors').text.lstrip('by ')
            except:
                pass
            # description
            data['course_description'] = driver.find_element_by_id('course-page-hero').find_element_by_tag_name(
                'p').text
            # What you'll learn
            data["What-you'll-learn"] = driver.find_element_by_class_name('course-page-section').text.lstrip(
                "What you'll learn\n")

            # course info
            info = driver.find_elements_by_class_name('course-content-right-container')[4].find_elements_by_class_name(
                'course-info-rows')
            for inf in info:
                if "Level" in inf.text:
                    # Level
                    data['level'] = inf.text.lstrip('Level\n')
                elif "Updated" in inf.text:
                    # Updated
                    data['updated'] = inf.text.lstrip('Updated\n')
                elif 'Duration' in inf.text:
                    # Duration
                    data['duration'] = inf.text.lstrip('Duration\n')
                elif 'Rating' in inf.text:
                    gray_star = len(inf.find_elements_by_class_name('gray'))
                    half_star = len(inf.find_elements_by_class_name('fa-star-half-o')) / 2
                    star = 5 - gray_star - half_star
                    data['rating'] = star

            try:
                # About the author
                data['About-the-author'] = driver.find_element_by_class_name('author-item').find_element_by_tag_name(
                    'p').text
            except:
                pass
            # table of content
            buttons = driver.find_elements_by_class_name('toc-item')
            # click on buttons

            try:
                for b in buttons:
                    b.click()
                    sleep(2)
            except:
                driver.find_element_by_class_name('cancel').click()
                for b in buttons:
                    b.click()
                    sleep(2)
            lessons = driver.find_elements_by_class_name('toc-item')
            lesson_data = {}
            for l in lessons:
                title = l.find_element_by_class_name('toc-title').text.split('\n')[0]
                li = l.find_element_by_class_name('toc-content').find_elements_by_tag_name('li')
                les_data = []
                for i in li:
                    les_data.append(i.text)
                lesson_data[title] = les_data
            data['table-of-content'] = str(lesson_data)

            data = pd.DataFrame(data, index=[0])
            all_data = pd.concat([all_data, data], ignore_index=True)
            print(f'scrapped link {count}')
            count += 1

        all_data.to_csv('pluralsight_course_data.csv')
        print('pluralsight_course_data.csv is stored')
        return all_data
    except Exception as e:
        print(e)
        all_data.to_csv('pluralsight_course_data.csv')
        print(f'data saved upto link {count - 1} in pluralsight_course_data.csv ')

    finally:
        with open('plural_value.txt', 'w') as file:
            file.write(str(count - 1))
        all_data.to_csv('pluralsight_course_data.csv')
        return all_data


if __name__ == "__main__":
    options = chrome_driver.ChromeOptions()
    options.add_argument("--start-maximized");
    options.headless = True
    driver = chrome_driver.Chrome(options=options)
    data = scrap_course(driver)