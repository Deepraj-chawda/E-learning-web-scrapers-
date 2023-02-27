import pandas as pd
import undetected_chromedriver.v2 as chrome_driver
from bs4 import BeautifulSoup
from os.path import exists
import warnings
warnings.filterwarnings("ignore")


def scrap(driver):

    file_link = exists('masterclass_links.csv')

    if file_link:

        d = pd.read_csv('masterclass_links.csv')
        urls = list(d.loc[:,'links'])
    else:
        print('masterclass_links.csv file not found')
        return pd.DataFrame({})

    try:
        file_exists = exists('masterclass_value.txt')
        if file_exists:
            with open('masterclass_value.txt', 'r') as file:
                value = int(file.read())
                count = value + 1

            all_data = pd.read_csv('masterclass_course_data.csv', index_col=0)

        else:
            value = 0
            all_data = pd.DataFrame(dict())
            count = 1

        if value == len(urls):
            print('Already Scrapped all links....')
            input_val = int(input('\nEnter 1 for scrapping again : '))
            if input_val == 1:
                value = 0
                count = 1
                all_data = pd.DataFrame(dict())



        for url in urls[value:]:
            data = dict()
            driver.get(url)

            s = BeautifulSoup(driver.page_source)

            # getting title

            data['title'] = s.find('h1',attrs={'class':'mc-text-h1 mc-mb-4'}).text

            inst = s.find('a', attrs={'class': 'mc-text--link'})
            if inst:
                data['Instructor'] = inst.text

                data['Instructor_class_link'] = 'https://www.masterclass.com' + inst['href']

            data['lesson_time'] = s.find('p',attrs={'class':'mc-mt-1 mc-text-small mc-text--muted'}).text

            data['Instructor_image'] = s.find('img',attrs={'class':'mc-corners--circle'})['src']

            data['rating'] = s.find('div',attrs={'class':'d-flex justify-content-between align-items-center'}).p.text

            data['topic_include'] = s.find('p',attrs={'class':'mc-text-small mc-text--muted'}).text

            data['about_instructor'] = s.find('p',attrs={'class':'mc-text--muted mc-pt-4'}).text

            lesson = s.find('nav', attrs={'class': 'mc-theme-dark mc-bg-dark mc-corners--rounded mc-py-5'}).find_all('li')
            lesson = [l.text for l in lesson]
            data['lesson_plan'] = str(lesson)

            data = pd.DataFrame(data, index=[0])
            all_data = pd.concat([all_data, data], ignore_index=True)
            print(f'scrapped link {count}')
            count += 1

        all_data.to_csv('masterclass_course_data.csv')
        print("masterclass_course_data.csv is stored")
        return all_data

    except Exception as e:
        print(e)
        all_data.to_csv('masterclass_course_data.csv')
        print(f'data saved upto link {count - 1} in masterclass_course_data.csv ')

    finally:
        with open('masterclass_value.txt', 'w') as file:
            file.write(str(count - 1))
        all_data.to_csv('masterclass_course_data.csv')
        return all_data


if __name__ == "__main__":
    options = chrome_driver.ChromeOptions()
    options.add_argument("--start-maximized");
    #options.headless = True
    driver = chrome_driver.Chrome(options=options)
    data = scrap(driver)

