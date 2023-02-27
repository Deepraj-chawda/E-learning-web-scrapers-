import requests
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
from bs4 import BeautifulSoup



def get_links():
    res = requests.get('https://www.futurelearn.com/sitemap.xml')
    soup = BeautifulSoup(res.content, ['xml'])
    links = soup.find_all('loc')

    topics = [link.text for link in links[-39:]]
    all_links = []
    for topic in topics:
        res = requests.get(topic)
        soup = BeautifulSoup(res.content, ['xml'])
        links = soup.find_all('loc')
        to_links = [link.text for link in links]
        all_links.extend(to_links)
        print('scrapping links..')

    return all_links

if __name__ == "__main__":
    all_links = get_links()
    all_links = pd.DataFrame(all_links, columns=['links'])
    all_links.drop_duplicates(subset="links", inplace=True)
    all_links.to_csv('topics_links.csv')