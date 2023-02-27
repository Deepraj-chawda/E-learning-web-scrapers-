from bs4 import BeautifulSoup
import pandas as pd
import undetected_chromedriver.v2 as chrome_driver
import warnings
warnings.filterwarnings("ignore")

def scrap(sitemap_link,specific_link,file_name):
    options = chrome_driver.ChromeOptions()
    options.add_argument("--start-maximized");
    options.headless = True
    driver = chrome_driver.Chrome(options=options)
    # get sitemap
    driver.get(sitemap_link)
    print('start scrapping links')
    # get all course links
    soup = BeautifulSoup(driver.page_source, ['xml'])
    links = soup.find_all('loc')
    links = [l.text for l in links if l.text.startswith(specific_link)]
    links = pd.DataFrame(links, columns=['links'])
    links.to_csv(file_name)
    print(f'scrapped all links and save it in {file_name}')
    # return links
    return links


if __name__ == "__main__":

    # Replace it with sitemap Link
    sitemap_link = 'https://www.pluralsight.com/sitemap.xml'
    # Replace it with start point of link whatever you want
    specific_link = 'https://www.pluralsight.com/courses/'
    # Repalce it with file name of csv (anything you want)
    file_name = 'courses_link.csv'
    data = scrap(sitemap_link,specific_link,file_name)