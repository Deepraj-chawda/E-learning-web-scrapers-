from bs4 import BeautifulSoup
import pandas as pd
import undetected_chromedriver.v2 as chrome_driver
import warnings
import time

warnings.filterwarnings("ignore")


def scrap_link(driver):
    links = []
    print('start..')
    # get requests on page
    driver.get('https://www.masterclass.com/sitemap')
    soup = BeautifulSoup(driver.page_source)

    rows = soup.find_all('div', attrs={"class": "col-8"})

    categories = rows[1].find_all('a')

    categories = ['https://www.masterclass.com' + c['href'] for c in categories]

    for cat in categories:
        driver.get(cat)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source)

        row = soup.find_all('li', attrs={'class': 'col-12 col-md-6'})
        sub_cat = ["https://www.masterclass.com" + r.a['href'] for r in row]

        for s in sub_cat:
            driver.get(s)
            soups = BeautifulSoup(driver.page_source)

            rows = soups.find_all('li', attrs={'class': 'col-12 col-md-6'})
            link = ["https://www.masterclass.com" + r.a['href'] for r in rows]
            print(len(link))

            links.extend(link)
            print('scrapping.......')

    links = pd.DataFrame(links, columns=['links'])
    links.drop_duplicates(subset="links", inplace=True)
    links.to_csv('masterclass_links.csv')
    print(f'scrapped all links and save it in masterclass_links.csv')
    # return links
    return links



if __name__ == "__main__":
    options = chrome_driver.ChromeOptions()
    options.add_argument("--start-maximized");
    options.headless = True
    driver = chrome_driver.Chrome(options=options)
    links = scrap_link(driver)
    print(len(links))