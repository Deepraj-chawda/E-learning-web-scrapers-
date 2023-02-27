from bs4 import BeautifulSoup
import pandas as pd
import undetected_chromedriver.v2 as chrome_driver
import warnings
import time

warnings.filterwarnings("ignore")


def scrap_link(driver):
    all_data = pd.DataFrame(dict())
    print('start..')

    # get requests on page
    driver.get('https://www.kaggle.com/learn')
    soup = BeautifulSoup(driver.page_source)

    links = soup.find('ul',attrs={'class':'km-list km-list--two-line'}).find_all('a')

    links = ['https://www.kaggle.com' + l['href'] for l in links]
    print('links scrapped')

    for link in links:
        data = dict()
        driver.get(link)
        time.sleep(2)
        s = BeautifulSoup(driver.page_source)

        data['title'] = s.find('h1').text

        data['text_under_title'] = s.find('span',attrs={'class':'sc-ezWOiH sc-bZkfAO sc-fEVxLL fuNBHd kxbrKq eXCSWg'}).text

        data['hours'] = s.find('div',attrs={'class':'sc-LAAhi cPQwaS'}).find('p',attrs={'class':'sc-cxabCf sc-llJcti bGyNSd hMXWEN'}).text

        divs = s.find_all('div', attrs={"class": "sc-kACOFk bMUtIw"})
        for d in divs:
            if 'Builds on' in d.text:

                data['Builds on'] = d.find('p', attrs={"class": "sc-cxabCf sc-llJcti ieLZFa hMXWEN"}).text
            elif 'Preparation for' in d.text:
                pre = d.find_all('p')
                pre = [p.text for p in pre]
                data['Preparation for'] = str(pre)



        data['Hours to earn certificate'] =  s.find_all('p',attrs={"class":"sc-cxabCf sc-llJcti ieLZFa hMXWEN"})[-3].text

        data['cost'] = s.find_all('p',attrs={"class":"sc-cxabCf sc-llJcti ieLZFa hMXWEN"})[-2].text

        data['Instructor'] = s.find_all('div',attrs={'class':"sc-kACOFk bMUtIw"})[-1].p.text

        data['Instructor_profile'] = 'https://www.kaggle.com' + s.find_all('div',attrs={'class':"sc-kACOFk bMUtIw"})[-1].a['href']

        les_data = {}
        lesson = s.find('ul', attrs={'class': "km-list km-list--three-line"}).find_all('li')

        for les in lesson:
            title = les.find('div', attrs={"class": "sc-izdjZO dZaKwp"}).text
            text = les.find('div',attrs={"class":"sc-dhmRnH iorhWL"}).text
            les_data[title] = text

        data['lessons'] = str(les_data)

        data = pd.DataFrame(data, index=[0])
        all_data = pd.concat([all_data, data], ignore_index=True)
        print(f'scrapped {link}')

    all_data.to_csv('kaggle_course_data.csv')
    print("kaggle_course_data.csv is stored")
    # return dATA
    return all_data



if __name__ == "__main__":
    options = chrome_driver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.headless = True
    driver = chrome_driver.Chrome(options=options)
    links = scrap_link(driver)
