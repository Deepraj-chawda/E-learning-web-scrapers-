import pandas as pd
import undetected_chromedriver.v2 as chrome_driver
from bs4 import BeautifulSoup
from os.path import exists
import warnings
warnings.filterwarnings("ignore")


def scrap(driver):
    print('start...')
    file_link = exists('hubspot_links.csv')

    if file_link:

        d = pd.read_csv('hubspot_links.csv')
        urls = list(d.loc[:,'links'])
    else:
        print('hubspot_links.csv file not found. Please Run the hubspotacademy_link.py')
        return pd.DataFrame({})

    try:
        file_exists = exists('hubspot_course_value.txt')
        if file_exists:
            with open('hubspot_course_value.txt', 'r') as file:
                value = int(file.read())
                count = value + 1

            all_data = pd.read_csv('hubspot_course_data.csv', index_col=0)

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
            title = s.find('h1',attrs={'class':'h2'})
            if title:
                data['title'] = title.text
            else:
                try:
                    data['title'] = s.find('div',attrs={'class':'academy-lesson-header__heading'}).h1.text
                except :
                    print(f'link {count} not found')
                    count += 1
                    continue

            price = s.find('p',attrs={'class':"academy-lesson-header__subheading"})
            if price:
                data['price'] = price.text

            des = s.find('p',attrs={"class":"academy-lesson-header__description"})
            if des:
                data['description'] = des.text

            who = s.find('div', attrs={"data-testid": "personas"})
            if who:
                who = who.find_all('li')
                who = [w.text for w in who]
                data['Who is this for'] = str(who)

            learn = s.find('div', attrs={"data-testid": "learnings"})
            if learn:
                learn = learn.find_all('li')
                learn = [l.text for l in learn]
                data["What you'll learn"] = str(learn)

            cour = s.find('div', attrs={"data-testid": "stats"})
            if cour:
                cour = cour.find_all('p')
                cour = [c.text for c in cour]
                data['Course Details'] = str(cour)

            tags = s.find('div', attrs={"data-testid": "tags"})
            if tags:
                tags = tags.find_all('li')
                tags = [t.text for t in tags]
                data['tags'] = str(tags)

            insts = s.find_all('div', attrs={'class': 'instructor-info__wrapper'})
            instructor = {}
            for ins in insts:
                instructor[ins.find('h2').text] = ins.find('p').text
            data['instructors'] = str(instructor)

            les = s.find_all('div', attrs={'class': 'sc-htpNat fTtYjk hsg-row-dropdown'})
            les = [l.text for l in les]
            data['Course_curriclum'] = str(les)


            data = pd.DataFrame(data, index=[0])
            all_data = pd.concat([all_data, data], ignore_index=True)
            print(f'scrapped link {count}')
            count += 1

        all_data.to_csv('hubspot_course_data.csv')
        print("hubspot_course_data.csv is stored")
        return all_data

    except Exception as e:
        print(e)
        all_data.to_csv('hubspot_course_data.csv')
        print(f'data saved upto link {count - 1} in hubspot_course_data.csv ')

    finally:
        with open('hubspot_course_value.txt', 'w') as file:
            file.write(str(count - 1))
        all_data.to_csv('hubspot_course_data.csv')
        return all_data


if __name__ == "__main__":
    options = chrome_driver.ChromeOptions()
    options.add_argument("--start-maximized");
    #options.headless = True
    driver = chrome_driver.Chrome(options=options)
    data = scrap(driver)

