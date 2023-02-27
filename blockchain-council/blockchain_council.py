import requests
from bs4 import BeautifulSoup
import pandas as pd
import undetected_chromedriver.v2 as chrome_driver
import warnings
import time
from os.path import exists
warnings.filterwarnings("ignore")


def scrap():
    print('start..')
    file_link = exists('blockchain_council_links.csv')

    if file_link:

        d = pd.read_csv('blockchain_council_links.csv')
        urls = list(d.loc[:, 'links'])
    else:

        urls = []

        url = 'https://www.blockchain-council.org'
        # get requests on page
        res = requests.get('https://www.blockchain-council.org')
        soup = BeautifulSoup(res.content)

        divs = soup.find_all('div', attrs={'class': 'nich-col-md-4'})

        for d in divs:
            urls.extend([a['href'] for a in d.find_all('a') if 'certifications' in a['href'] or 'online-degree' in a['href']])
            print('scrapping.......')

        links = pd.DataFrame(urls, columns=['links'])
        links.drop_duplicates(subset="links", inplace=True)
        links.to_csv('blockchain_council_links.csv')
        print(f'scrapped all links and save it in blockchain_council_links.csv')

    all_data = pd.DataFrame(dict())
    count = 1
    for url in urls:
        try:
            res = requests.get(url)
            s = BeautifulSoup(res.content)
            data = dict()
            try:

                data['title'] = s.find('h1').text
            except:
                print(f'{url} not found')
                count += 1
                continue
            para = s.find('div', attrs={'class': 'pdt-single-content'}).find_all('p')
            about = ''
            for p in para:
                about += p.text
            data['about'] = about

            lists = s.find('ul', attrs={'class': 'pdt-metas'}).find_all('li')
            for l in lists:
                data[l.span.text.strip()] = l.h3.text.strip()

            data['price'] = s.find('div',attrs={'class':'pdt-single-price'}).h3.text

            div = s.find_all('div', attrs={'class': 'elementor-widget-wrap elementor-element-populated'})
            try:
                mod = div[3].find('div',attrs={"class":"elementor-accordion"})
                less = mod.find_all('div', attrs={'class': 'elementor-accordion-item'})
                benefit = div[5].find_all('li')
                gets = div[7].find_all('li')
                data['Career Facts'] = div[9].text.strip()

                data['Final Outcome'] = div[11].text.strip()
            except:
                mod = div[2].find('div', attrs={"class": "elementor-accordion"})
                less = mod.find_all('div', attrs={'class': 'elementor-accordion-item'})
                benefit = div[4].find_all('li')
                gets = div[6].find_all('li')
                data['Career Facts'] = div[8].text.strip()

                data['Final Outcome'] = div[10].text.strip()

            les_data = {}

            for l in less:
                title = l.find('div', attrs={'class': 'elementor-tab-title'}).a.text
                parts = l.find('div', attrs={'class': 'elementor-tab-content elementor-clearfix'}).find_all('li')
                parts = [p.text for p in parts]
                les_data[title] = parts

            data['Modules Included'] = str(les_data)


            benefit = [b.text.strip() for b in benefit]
            data['Certification Benefits'] = str(benefit)


            gets = [g.text.strip() for g in gets]
            data['What You Get'] = str(gets)



            dd = s.find_all('div', attrs={'class': 'elementor-widget-container'})
            grow = dd[19].find_all('li')
            grow = [g.text.strip() for g in grow]
            data['The Growth Curve Ahead'] = str(grow)
            data['domains'] = dd[21].text.strip()

            story = s.find_all('div', attrs={'class': 'item'})
            st_data = {}
            for st in story:
                st_data[st.h3.text] = st.p.text
            data['Success Stories'] = str(st_data)

            data = pd.DataFrame(data, index=[0])
            all_data = pd.concat([all_data, data], ignore_index=True)
        except :
            print(f'unable to scrap link {url}')
            continue
        finally:
            print(count)
            count += 1
    all_data.to_csv('blockchain_course_data.csv')
    print("blockchain_course_data.csv is stored")


if __name__ == "__main__":

    scrap()
