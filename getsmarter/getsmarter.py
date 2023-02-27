import time

import pandas as pd
import undetected_chromedriver.v2 as chrome_driver
from bs4 import BeautifulSoup
from os.path import exists
import warnings
warnings.filterwarnings("ignore")


def scrap(driver):

    file_link = exists('getsmarter_links.csv')

    if file_link:

        d = pd.read_csv('getsmarter_links.csv')
        links = list(d.loc[:,'links'])
    else:
        links = []

        # get requests on page
        for i in range(1,17):
            driver.get(f'https://www.getsmarter.com/products/view-all?page={i}')
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source)

            urls = soup.find_all('a',attrs={'class':"display-block"})
            urls = ['https://www.getsmarter.com' + a['href'] for a in urls]
            links.extend(urls)
            print(f'scrapped....... page {i}')

        links_d = pd.DataFrame(links, columns=['links'])
        links_d.drop_duplicates(subset="links", inplace=True)
        links_d.to_csv('getsmarter_links.csv')
        print(f'scrapped all links and save it in getsmarter_links.csv')

    try:
        print('start..')
        file_exists = exists('getsmarter_value.txt')
        if file_exists:
            with open('getsmarter_value.txt', 'r') as file:
                value = int(file.read())
                count = value + 1

            all_data = pd.read_csv('getsmarter_course_data.csv', index_col=0)

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

        for url in links[value:]:

            data = dict()
            driver.get(url)

            s = BeautifulSoup(driver.page_source)

            # getting title

            data['title'] = s.find('h1',attrs={'class':'course-name-heading'}).text

            data['about'] = s.find('p',attrs={'class':'paragraph-default course-paragraph'}).text

            data['University name'] = s.find('p',attrs={'class':'paragraph-small-blue course-partner-name'}).text
            data['University image'] = s.find('img',attrs={'class':'course-logo'})['src']

            try:
                data['start_date'] = s.find('div',attrs={'class':'start-date'}).find('p',attrs={'class':"heading-h5"}).text
            except:
                data['start_date'] = s.find('p',attrs={'class':"heading-h3"}).text
            div = s.find_all('div',attrs={'class':'course-info-block'})
            data['price'] = div[1].find('p',attrs={'class':"heading-h3"}).text

            info = s.find('div', attrs={'class': 'row offset'}).find_all('div', attrs={'class': 'course-info-block'})
            for c in info:
                try:
                    t = c.find('p',attrs={"class":'paragraph-small'}).text
                    data[t] = c.find('p',attrs={"class":'heading-h5'}).text
                except:
                    pa = [p.text for p in mods[0].find_all('p') if p.text]
                    data[pa[0]] = pa[1]

            data['Course overview'] = s.find('div',attrs={"class":"content"}).text

            mods = s.find('div', attrs={'class': 'curriculum'}).find('div',
                                                                     attrs={'class': 'modules-container'}).find_all('div', attrs={'class': 'module-block'})
            mod_data = {}
            for m in mods:
                tit = m.find('p',attrs={'class':'heading font-h6-mobile'}).text
                mod_data[tit] = m.find('p',attrs={'class':'font-p-default'}).text

            data['Course curriculum'] = str(mod_data)

            try:
                inst = s.find_all('div', attrs={"class": "faculty-director"})
                d_ins = {}
                for ins in inst:
                    d_ins[ins.find('p',attrs={"class":"name"}).text] = [ins.find_all('p')[-2].text,ins.img['data-original']]
                data['Convenors'] = str(d_ins)
            except:
                pass

            para = s.find_all('div', attrs={"class": "paragraph"})
            data['What will set you apart']= str([p.text for p in para])

            data['About the certificate'] = s.find('div',attrs={"class":"certificate-section"}).find('div',attrs={"class":"blurb"}).text
            try:
                data['What past students think'] = str({s.find('div',attrs={'class':'testimonial-name-block'}).text:s.find('div',attrs={'class':'testimonial-text'}).text})
            except:
                pass
            data = pd.DataFrame(data, index=[0])
            all_data = pd.concat([all_data, data], ignore_index=True)
            print(f'scrapped link {count}')
            count += 1

        all_data.to_csv('getsmarter_course_data.csv')
        print("getsmarter_course_data.csv is stored")
        return all_data

    except Exception as e:
        print(e,url)
        all_data.to_csv('getsmarter_course_data.csv')
        print(f'data saved upto link {count - 1} in getsmarter_course_data.csv ')

    finally:
        with open('getsmarter_value.txt', 'w') as file:
            file.write(str(count - 1))
        all_data.to_csv('getsmarter_course_data.csv')
        return all_data


if __name__ == "__main__":
    options = chrome_driver.ChromeOptions()
    options.add_argument("--start-maximized");
    #options.headless = True
    driver = chrome_driver.Chrome(options=options)
    data = scrap(driver)

