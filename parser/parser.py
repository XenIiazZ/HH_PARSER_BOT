import pymysql.cursors
import requests
from bs4 import BeautifulSoup
import fake_useragent
import time
import json
import pymysql
import mysql.connector
import lxml
import re


config ={
    'user': 'root',
    'password': 'DoLlitoS640M',
    'host': 'db',
    'database': 'hh_data',
   
}
    # Создание соединения с MySQL
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()
# Создание таблицы
create_table_query = """
    CREATE TABLE IF NOT EXISTS resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    salary VARCHAR(255),
    education VARCHAR(255),
    employment_type VARCHAR(255),
    schedule VARCHAR(255),
    work_experience VARCHAR(255),
    search_status VARCHAR(255),
    location VARCHAR(255),
    link VARCHAR(255),
    tags TEXT
)
"""
create_table_query = """
    CREATE TABLE IF NOT EXISTS vacancies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    salary VARCHAR(255),
    experience VARCHAR(255),
    schedule VARCHAR(255),
    skills TEXT,
    address VARCHAR(255),
    vacancy_date VARCHAR(255),
    tags TEXT
)
"""
cursor.execute(create_table_query)


def get_links(text):
    ua = fake_useragent.UserAgent()
    data = requests.get(
        
        url = f"https://hh.ru/search/resume?text={text}&area=2&isDefaultArea=true&exp_period=all_time&logic=normal&pos=full_text&page=1",
        headers = {"user-agent":ua.random}

    )
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, "lxml")
    try:
        page_count = int(soup.find("div", attrs={"class":"pager"}).find_all("span", recursive=False)[-1].find("a").find("span").text)
    except:
        return
    for page in range(page_count):
        try:
            data = requests.get(
            url = f"https://hh.ru/search/resume?text={text}&area=2&isDefaultArea=true&exp_period=all_time&logic=normal&pos=full_text&page={page}",
            headers = {"user-agent":ua.random})
            if data.status_code != 200:
                continue
            soup = BeautifulSoup(data.content, "lxml")
             
            for a in soup.find_all("a", attrs={"rel":"nofollow"}):
                yield f"https://hh.ru{a.attrs['href'].split('?')[0]}"
        except Exception as e:
            print(f"{e}")
        time.sleep(1)


def get_resume(link_resume):
    ua = fake_useragent.UserAgent()
    data = requests.get(
        url=link_resume,
        headers={"user-agent":ua.random}
    )
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, "lxml")
    try:
        name = soup.find(attrs={"class":"resume-block__title-text"}).text
    except: name =""
    try:
        salary = soup.find(attrs={"class":"resume-block__salary"}).text.replace("\u2009","").replace("\xa0","")
    except: salary =""
    try:
        search_status = soup.find(attrs={"class":"label--rWRLMsbliNlu_OMkM_D3 label_light-green--oMhc5Pq9VsjySzrrLOTh"}).text
    except: search_status =""
    try:
        tags= [tag.text for tag in soup.find(attrs={"class":"bloko-tag-list"}).find_all(attrs={"class":"bloko-tag__section_text"})]
    except:
        tags=[]
    try:
        education = soup.find(attrs={"class":"bloko-link bloko-link_kind-tertiary"}).text
    except: education =""
    try:
        work_experience = soup.find(attrs={"class":"resume-block__title-text resume-block__title-text_sub"}).text.replace(" ","")
    except: work_experience =""
    try:
        location = soup.find(attrs={"class":"bloko-translate-guard"}).text.replace(" ","")
    except: location =""
    try:
        schedule = soup.find(attrs={"class":"resume-block-container"}).find_all("p")[1].text
        
    except: schedule =""
    try:
        employment_type = soup.find(attrs={"class":"resume-block-container"}).find_all("p")[0].text
        
    except: employment_type =""
    try:
        link = link_resume
        
    except: link =""
    
    resume = {
        "name":name,
        "salary":salary,
        "education":education,
        "employment_type":employment_type,
        "schedule":schedule,
        "work_experience":work_experience,
        "search_status":search_status,
        "location":location,
        "link": link,
        "tags":tags

    }
    return resume
data = []
for a in get_links("python"):
    if not "/search/" in a:
    
        resume = get_resume(a)
        data.append(resume)
        time.sleep(1)
        # Загрузка в базу данных
        insert_query = """
            INSERT INTO resumes (name, salary, education, employment_type, schedule, work_experience, search_status, location, link, tags)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        tags_string = ', '.join(resume['tags'])
        values = (resume['name'], resume['salary'], resume['education'],
                resume['employment_type'], resume['schedule'], resume['work_experience'],
                resume['search_status'], resume['location'], resume['link'], tags_string)

        cursor.execute(insert_query, values)
        cnx.commit()

def get_link(text):
    """Функция для получения ссылок на вакансии
    в соответствии с подаваемыми в неё ключевыми словами"""
    
    ua = fake_useragent.UserAgent() # для передачи заголовка
    data = requests.get(
        url=f"https://hh.ru/search/vacancy?text={text}&area=113&page=1",
        
        headers={"user-agent":ua.random} # создаём заголовок, передаём ему случайный заголовок из созданного объекта
    )
    
    if data.status_code != 200: # то есть, если код обработки запроса не 200 (есть ошибки), то выходим из функции
        return
    
    soup = BeautifulSoup(data.content, "lxml") # передаём контент страницы
    
    try:
        page_count = int(soup.find("div", attrs={"class":"pager", "data-qa":"pager-block"})\
                         .find_all("span", recursive=False)[-1].find("a").find("span").text)
        # считаем количество страниц в соответствующем поисковом запросе на сайте
    except:
        return
    
    for page in range(page_count): # проходим циклом по каждой странице, чтобы получить ссылки на вакансии
        try:   
            data = requests.get(
                url=f"https://hh.ru/search/vacancy?L_save_area=true&text={text}&search_field=\
                name&excluded_text=&area=113&salary=&currency_code=RUR&experience=doesNotMatter&order_by=\
                relevance&search_period=0&items_on_page=50&page={page}",
                
                headers={"user-agent":ua.random} # создаём заголовок, передаём ему случайный заголовок из созданного объекта
                ),
            
            
            if data.status_code != 200:
                continue
                
            soup = BeautifulSoup(data.content, "lxml") # считываем контент страницы
            
            for a in soup.find_all("a",attrs={"class":"bloko-link", "target":"_blank"}):
                yield f"{a.attrs['href'].split('?')[0]}"
                    
        except Exception as e:
            print(f"{e}")

            continue
        time.sleep(1)
def get_vacancy(link):
    ua = fake_useragent.UserAgent()
    data = requests.get(
        url=link,
        headers={"user-agent":ua.random}
    )
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, "lxml")
    try:
        tags= [tag.text for tag in soup.find(attrs={"class":"bloko-tag-list"}).find_all(attrs={"class":"bloko-tag__section_text"})]
    except:
        tags=[]
    
    try:
        name = soup.find(attrs={"class":"vacancy-title"}).text.replace("от"," от ").replace("до"," до ")
    except:
        name = ""
    # зарплата
    try:
        salary = soup.find(attrs={"data-qa":"vacancy-salary-compensation-type-net"}).text.replace("\xa0","")
    except:
        salary = ""
    # опыт работы
    try:
        experience = soup.find(attrs={"class":"vacancy-description-list-item"}).text.replace("Требуемый опыт работы: ","")
    except:
        experience = ""
    # режим работы
    try:
        schedule = soup.find(attrs={"class":"vacancy-description-list-item", "data-qa":"vacancy-view-employment-mode"}).text
    except:
        schedule = ""
    # требуемые навыки
    try:
        skills = [skills.text for skills in soup.find(attrs={"class":"bloko-tag-list"})\
                                                    .find_all(attrs={"class":"bloko-tag__section bloko-tag__section_text",\
                                                    "data-qa":"bloko-tag__text"})]
    
    except:
        skills = ""
    # адрес
    try:
        address = soup.find(attrs={"data-qa":"vacancy-address-with-map", "class":"bloko-text bloko-text_large"}).text
    
    except:
        address = ""
    # дата публикации вакансии
    try:
        vacancy_date = soup.find(attrs={"class":"vacancy-creation-time-redesigned"}).text.replace("Вакансия опубликована ","")\
        .replace("\xa0"," ")
    
    except:
        vacancy_date = ""
    vacancy = {
        "name":name,
        "salary":salary,
        "experience":experience,
        "schedule":schedule,
        "skills":skills,
        "address":address,
        "vacancy_date":vacancy_date,
        "tags":tags

    }
    return vacancy
# Загрузка данных

data1 = []
for a in get_link("python"):
    if "/vacancy/" in a:
            vacancy = get_vacancy(a)
            data1.append(vacancy)
            time.sleep(1)
            
            # Загрузка в базу данных
            insert_query = """
            INSERT INTO vacancies(name,salary,experience,schedule,skills,address,vacancy_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            tags_string = ', '.join(vacancy['tags'])
            values = (vacancy['name'], vacancy['salary'], vacancy['experienc'],
              vacancy['schedule'], vacancy['skills'], vacancy['address'],
              vacancy['vacancy_date'],tags_string)
            
            cursor.execute(insert_query, values)
            cnx.commit()
            
cursor.close()
cnx.close()

