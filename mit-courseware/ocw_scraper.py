import undetected_chromedriver.v2 as chrome_driver
import pandas as pd
import warnings

warnings.filterwarnings("ignore")
from bs4 import BeautifulSoup


def scrap_links(driver):
    driver.get('https://ocw.mit.edu/sitemap.xml')

    soup = BeautifulSoup(driver.page_source, ['xml'])
    links = soup.find_all('loc')
    links = [l.text.rstrip('sitemap.xml') for l in links[1:]]
    return links


def scrap_data(driver):
    # get links
    links = scrap_links(driver)
    print('links scrapped')
    all_data = pd.DataFrame(dict())
    count = 1
    for link in links:
        data = dict()
        # get request on page
        driver.get(link)
        # title
        data['title'] = driver.find_element_by_id('course-banner').text
        # course-description
        data['course-description'] = driver.find_element_by_id('course-description').text

        soup = BeautifulSoup(driver.page_source)
        table = soup.find_all('table', attrs={'id': 'course-info-table'})[1]
        trs = table.find_all('tr')
        for row in trs:
            tds = row.find_all('td')
            title = tds[0].text.strip(':')
            li = tds[1].find_all('li')
            if li:
                data[title] = str([i.text.strip().replace('\n', '') for i in li])
            else:
                data[title] = tds[1].text.strip()

        # Learning Resource Types
        col = soup.find_all('div', attrs={'class': 'col-6 col-xl-3'})
        data['learning-resource-types'] = str([c.find('span').text.strip() for c in col])

        # other pages links
        contents = soup.find_all('li', attrs={'class': 'course-nav-list-item'})
        pages = set()
        for i in contents:
            pages.add(i.text.strip().lower().replace(' ', '-'))
        pages = list(pages)
        for page in pages:
            try:
                driver.get(link + page)
                soup = BeautifulSoup(driver.page_source)
                data[page] = soup.find('main', attrs={'id': 'course-content-section'}).text
            except:
                continue
        data = pd.DataFrame(data, index=[0])
        all_data = pd.concat([all_data, data], ignore_index=True)
        print(f'scrapped link {count}')
        count += 1

    all_data.to_csv('ocw_course_data.csv')
    print('ocw_course_data.csv is stored')
    return all_data


if __name__ == "__main__":
    options = chrome_driver.ChromeOptions()
    options.add_argument("--start-maximized");
    options.headless = True
    driver = chrome_driver.Chrome(options=options)
    data = scrap_data(driver)