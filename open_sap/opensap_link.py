from bs4 import BeautifulSoup
import pandas as pd
import undetected_chromedriver.v2 as chrome_driver
import warnings
import time
warnings.filterwarnings("ignore")

def scrap_link(driver):
    links = []
    # get requests on page
    driver.get("https://open.sap.com/courses")
    print('start scrapping links')
    # get all course links
    i =0
    while True:
        try :
            driver.find_element_by_class_name('load-more').click()
            time.sleep(3)
        except Exception as e:

            break
        i += 1
        print(i)
        print('loading more .....')

    time.sleep(3)
    soup = BeautifulSoup(driver.page_source)

    courses = soup.find_all('div', attrs={'class': "course-card course-card--expanded"})

    for c in courses:
        l = c.find('a', attrs={"class": "course-card__image"})['href']
        links.append('https://open.sap.com' + l)

    links = pd.DataFrame(links, columns=['links'])
    links.to_csv('opensap_links.csv')
    print(f'scrapped all links and save it in opensap_links.csv')
    # return links
    return links


if __name__ == "__main__":
    options = chrome_driver.ChromeOptions()
    options.add_argument("--start-maximized");
    options.headless = True
    driver = chrome_driver.Chrome(options=options)
    links = scrap_link(driver)
    print(len(links))