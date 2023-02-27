from bs4 import BeautifulSoup
import pandas as pd
import undetected_chromedriver.v2 as chrome_driver
import warnings
import time

warnings.filterwarnings("ignore")


def scrap_link(driver):
    links = []
    print('start..')
    url = 'https://in.mathworks.com/learn/training/classroom-courses.html?q=&page={}'
    # get requests on page
    for i in range(1,7):
        driver.get(url.format(i))
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source)

        cour = soup.find_all('div', attrs={'class': 'col-xs-12 col-sm-6 col-md-4'})
        link = [c.find('a')['href'] for c in cour]

        print(len(link))

        links.extend(link)
        print('scrapping.......')

    links = pd.DataFrame(links, columns=['links'])
    links.drop_duplicates(subset="links", inplace=True)
    links.to_csv('matlab_links.csv')
    print(f'scrapped all links and save it in matlab_links.csv')
    # return links
    return links



if __name__ == "__main__":
    options = chrome_driver.ChromeOptions()
    options.add_argument("--start-maximized");
    options.headless = True
    driver = chrome_driver.Chrome(options=options)
    links = scrap_link(driver)
    print(len(links))