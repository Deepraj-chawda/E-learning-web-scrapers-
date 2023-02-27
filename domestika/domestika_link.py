import requests
import bs4
import pandas as pd

def get_links():
    all_links = []
    print('srapping.......')
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
    res = requests.get('https://www.domestika.org/sitemap.xml', headers=headers)
    soup = bs4.BeautifulSoup(res.content, ['xml'])
    cours = soup.find_all('loc')
    cours = [l.text for l in cours if l.text.startswith('https://www.domestika.org/sitemap-courses-')]

    for c in cours:
        r = requests.get(c,headers=headers)
        soup = bs4.BeautifulSoup(r.content, ['xml'])
        link = soup.find_all('loc')
        link = [l.text for l in link  if l.text.startswith('https://www.domestika.org/en/')]
        all_links.extend(link)
        print('scrapping...')
    all_links = pd.DataFrame(all_links, columns=['links'])
    all_links.to_csv('domestika_links.csv')


if __name__ == "__main__":
    get_links()
    print('links stored in domestika_links.csv')