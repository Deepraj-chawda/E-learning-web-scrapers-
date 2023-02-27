import pandas as pd
import undetected_chromedriver.v2 as chrome_driver
from bs4 import BeautifulSoup
from os.path import exists
import warnings
warnings.filterwarnings("ignore")


def scrap(driver):

    file_link = exists('matlab_links.csv')

    if file_link:

        d = pd.read_csv('matlab_links.csv')
        urls = list(d.loc[:,'links'])
    else:
        print('matlab_links.csv file not found')
        return pd.DataFrame({})

    try:
        file_exists = exists('matlab_value.txt')
        if file_exists:
            with open('matlab_value.txt', 'r') as file:
                value = int(file.read())
                count = value + 1

            all_data = pd.read_csv('matlab_course_data.csv', index_col=0)

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
            data['title'] = s.find('h1',attrs={"class":"add_padding_top_40"}).text

            divs = s.find('div', attrs={'class': "col-xs-12 col-sm-4"}).find_all('div', attrs={
                'class': 'panel add_background_color_gray add_padding_top_5 add_padding_bottom_5'})

            for d in divs:
                if 'Level' in d.text:
                    data['level'] = d.p.text.strip().replace('\t', '')
                elif 'Prerequisites' in d.text:
                    data['Prerequisites'] = str([l.text for l in d.find_all('li')])
                elif 'Duration' in d.text:
                    data['Duration'] = d.p.text.strip().replace('\t', '')
                elif 'Languages' in d.text:
                    data['Languages'] = d.p.text.strip().replace('\t', '')

            data['Course Details'] = s.find('div', attrs={'class': "col-xs-12 col-sm-8"}).find('div', attrs={"class": "add_margin_40"}).text

            data['days details'] = s.find('div',attrs={'class':"col-xs-12 col-sm-8"}).find('div',attrs={"class":"mainParsys2 parsys containsResourceName resourceClass-parsys"}).text

            data = pd.DataFrame(data, index=[0])
            all_data = pd.concat([all_data, data], ignore_index=True)
            print(f'scrapped link {count}')
            count += 1

        all_data.to_csv('matlab_course_data.csv')
        print("matlab_course_data.csv is stored")
        return all_data

    except Exception as e:
        print(e)
        all_data.to_csv('matlab_course_data.csv')
        print(f'data saved upto link {count - 1} in matlab_course_data.csv ')

    finally:
        with open('matlab_value.txt', 'w') as file:
            file.write(str(count - 1))
        all_data.to_csv('matlab_course_data.csv')
        return all_data


if __name__ == "__main__":
    options = chrome_driver.ChromeOptions()
    options.add_argument("--start-maximized");
    #options.headless = True
    driver = chrome_driver.Chrome(options=options)
    data = scrap(driver)

