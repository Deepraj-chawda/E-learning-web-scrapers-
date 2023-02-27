import undetected_chromedriver.v2 as chrome_driver
import pandas as pd
import warnings
from os.path import exists

warnings.filterwarnings("ignore")
from bs4 import BeautifulSoup
from time import sleep

def get_link(driver):
    with open('microsoft learn.txt', 'r') as file:
        links = file.read().split()
    try:
        file_exists = exists('microsoft_link_value.txt')
        if file_exists:
            with open('microsoft_link_value.txt', 'r') as file:
                value= int(file.read())

                count = value + 1

            d = pd.read_csv('microsoft_links.csv', index_col=0)
            all_links = list(d['links'])

            if value == len(all_links) and value != 0:
                print('Already Scrapped all links....')
                input_val = int(input('\nEnter 1 for scrapping again : '))
                if input_val == 1:
                    value = 0
                    count = 1
                    all_links = []

        else:
            value = 0
            all_links = []
            count = 1


        for link in links[value:]:
            driver.get(link)
            sleep(3)
            soup = BeautifulSoup(driver.page_source)
            li = soup.find_all('a', attrs={"class": 'card-content-title'})

            c_link = []
            for l in li:

                c_link.append('https://docs.microsoft.com' + l['href'])
            all_links.extend(c_link)

            count += 1
            print(f'page {link} scrapped')

        all_links = pd.DataFrame(all_links, columns=['links'])
        all_links.drop_duplicates(subset="links", inplace=True)
        all_links.to_csv('microsoft_links.csv')

        return all_links

    except Exception as e:
        print(e)
        all_links = pd.DataFrame(all_links, columns=['links'])
        all_links.drop_duplicates(subset="links", inplace=True)
        all_links.to_csv('microsoft_links.csv')
        print(f'data saved upto link {count - 1} in microsoft_links.csv')

    finally:
        with open('microsoft_link_value.txt', 'w') as file:
            file.write(f'{str(count - 1)}')

        all_links = pd.DataFrame(all_links, columns=['links'])
        all_links.drop_duplicates(subset="links", inplace=True)
        all_links.to_csv('microsoft_links.csv')

        return all_links

if __name__ == "__main__":
    options = chrome_driver.ChromeOptions()
    options.add_argument("--start-maximized");

    # options.headless = True
    driver = chrome_driver.Chrome(options=options)
    all_links = get_link(driver)

