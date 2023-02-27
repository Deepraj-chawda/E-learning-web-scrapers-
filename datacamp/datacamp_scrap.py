import undetected_chromedriver.v2 as chrome_driver
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
from bs4 import BeautifulSoup


def scrap(link,driver):
    driver.get(link)
    data = dict()
    #getting title
    data['title'] = driver.find_element_by_class_name('css-19cs3ms-CoursePage').text
    
    span = driver.find_element_by_class_name('css-17kyv44-CoursePage').find_elements_by_class_name('css-10z9yxq-Stat')
    for s in span:
        text = s.text
        if text.endswith("Hours"):
            data['time_in_hours'] = text.rstrip(" Hours")
        elif text.endswith('Videos'):
            data['no_of_videos'] = text.rstrip(' Videos')
        elif text.endswith('Exercises'):
            data['Exercises'] = text.rstrip(' Exercises')
        elif text.endswith('Learners'):
            data['no_of_Learners'] = text.rstrip(' Learners')
        elif text.endswith('XP'):
            data['XP'] = text.rstrip(' XP')
    
    data['course-description'] = driver.find_element_by_class_name('css-1746fd2-CoursePage').text
    
    page_data = BeautifulSoup(driver.page_source)
    lessons = page_data.find_all('li',attrs={'class':"css-vurnku"})
    for i in range(len(lessons)):
        points = lessons[i].find('div',attrs={"class":"css-15sj5uq"}).find_all('span',attrs={'class':'css-1rbq0za'})
        data[f'what-you-will-learn-lesson-{i+1}'] = ','.join([p.text for p in points])
    
    footer =driver.find_element_by_class_name('css-5is1tl-CoursePage')
    collaborators = footer.find_elements_by_class_name('css-x9g3z1-CoursePage')
    prerequisities = footer.find_elements_by_class_name('css-1p8s5oy-CoursePage')
    
   
    data['collaborators'] = ','.join([collab.text  for collab in collaborators])
    data['prerequisities'] = ','.join([pre.text for pre in prerequisities])
    
    data = pd.DataFrame(data,index=[0])
    return data


def get_links(driver):
    driver.get('https://www.datacamp.com/sitemap/courses.xml')

    soup = BeautifulSoup(driver.page_source, ['xml'])
    links = soup.find_all('loc')
    all_data = pd.DataFrame(dict())
    i = 1
    for link in links:
        data = scrap(link.text,driver)
        all_data = pd.concat([all_data,data],ignore_index=True)
        print(f'link {i} scrapped')
        i += 1
    return all_data

if __name__ == "__main__":
    options = chrome_driver.ChromeOptions()
    options.add_argument("--start-maximized");
    options.headless = True
    driver = chrome_driver.Chrome(options=options)
    data = get_links(driver)
    data.to_csv('datacamp.csv')
    print('datacamp.csv is stored')
