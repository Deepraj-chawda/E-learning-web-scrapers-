import undetected_chromedriver.v2 as chrome_driver
import pandas as pd
import warnings
from os.path import exists

warnings.filterwarnings("ignore")
from bs4 import BeautifulSoup
from time import sleep

def get_link(driver):
    print('start..')
    file_link = exists('topics_links.csv')
    if file_link:
        d = pd.read_csv('topics_links.csv', index_col=0)
        links = list(d['links'])
    else:

        print('Run udemy_topics.py first')

    try:
        file_exists = exists('udemy_link_value.txt')
        if file_exists:
            with open('udemy_link_value.txt', 'r') as file:
                value, page_count = map(int,file.read().split(' '))

                count = value + 1

            d = pd.read_csv('courses_links_udemy.csv', index_col=0)
            all_links = list(d['links'])

            if value == len(all_links) and value != 0:
                print('Already Scrapped all links....')
                input_val = int(input('\nEnter 1 for scrapping again : '))
                if input_val == 1:
                    value = 0
                    count = 1
                    page_count = 1
                    all_links = []

        else:
            value = 0
            all_links = []
            count = 1
            page_count = 1

        for link in links[value:]:
            driver.get(f'{link}?p=1&ratings=4.0&sort=popularity')
            sleep(10)
            soup = BeautifulSoup(driver.page_source)

            page = soup.find('span', attrs={'class': 'pagination--page--1H0A2'})
            if not page:
                print("p",page)
                page = soup.find_all('a', attrs={'class': 'pagination--page--1H0A2'})
                if page:
                    page = page[-1].text
                else:
                    page=1

            else:
                page = page.text
            page_value = page_count
            for p in range(page_value,int(page)+1):

                driver.get(f'{link}?p={p}&ratings=4.0&sort=popularity')
                sleep(5)
                soup = BeautifulSoup(driver.page_source)
                divs = soup.find_all('div', attrs={'class': "popper--popper--2r2To"})[3:]
                link_p = []
                for div in divs:

                    r = div.find('span', attrs={'class': "udlite-text-xs course-card--reviews-text--1yloi"})
                    if r:

                        r = r.text[1:-1].replace(',', '')

                        if int(r) >= 100:

                            li = div.find('a')['href']
                            link_p.append('https://www.udemy.com'+li)

                all_links.extend(link_p)
                print(f'page no {page_count}')
                page_count += 1


            page_count = 1


            count += 1
            print(f'page {link} scrapped')

        return all_links

    except Exception as e:
        print(e)
        all_links = pd.DataFrame(all_links, columns=['links'])
        all_links.drop_duplicates(subset="links", inplace=True)
        all_links.to_csv('courses_links_udemy.csv')
        print(f'data saved upto link {count - 1} pages {page_count-1} in courses_links_udemy.csv')

    finally:
        with open('udemy_link_value.txt', 'w') as file:
            file.write(f'{str(count - 1)} {page_count}')

        all_links = pd.DataFrame(all_links, columns=['links'])
        all_links.drop_duplicates(subset="links", inplace=True)
        all_links.to_csv('courses_links_udemy.csv')

        return all_links

if __name__ == "__main__":
    options = chrome_driver.ChromeOptions()
    options.add_argument("--start-maximized");

    #options.headless = True
    driver = chrome_driver.Chrome(options=options)
    all_links = get_link(driver)
