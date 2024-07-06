import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
import fake_useragent
import time


# Токен бота
API_TOKEN = '7301863423:AAEhs6eCB7QXFgIbxrweJ4Sk0cBYx_UOv7I'
# Адрес сервиса аналитики
ANALYTICS_URL = 'http://backend:8001/analytics'

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    itembtn1 = types.KeyboardButton('Поиск вакансии')
    itembtn2 = types.KeyboardButton('Аналитика')
    markup.add(itembtn1,itembtn2)
    bot.send_message(message.chat.id, "Добро пожаловать! Это бот для парсинга вакансий на HH.ru. Выберите действие:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Поиск вакансии')
def search_vacancy(message):
    bot.send_message(message.chat.id, "Введите название вакансии, которую вы хотите найти:")
    bot.register_next_step_handler(message, process_vacancy_search)

def process_vacancy_search(message):
    search_text = message.text
    vacancies = get_vacancies(search_text)
    if vacancies:
        for vacancy in vacancies:
            text = f"Вакансия: {vacancy['title']}\n" \
                   f"Зарплата: {vacancy['salary']}\n" \
                   f"Опыт работы: {vacancy['experience']}\n" \
                   f"Тип занятости: {vacancy['employment_type']}\n" \
                   f"График работы: {vacancy['schedule']}\n" \
                   f"Местоположение: {vacancy['location']}\n" \
                   f"Ссылка: {vacancy['link']}\n" \
                   f"Теги: {', '.join(vacancy['tags'])}"
            bot.send_message(message.chat.id, text)
    else:
        bot.send_message(message.chat.id, "Вакансии по данному запросу не найдены.")

def get_vacancies(search_text):
    ua = fake_useragent.UserAgent()
    vacancies = []
    for page in range(1, 6):  # Проверяем максимум 5 страниц
        try:
            data = requests.get(
                url=f"https://hh.ru/search/vacancy?text={search_text}&area=2&isDefaultArea=true&page={page}",
                headers={"user-agent": ua.random}
            )
            if data.status_code != 200:
                continue
            soup = BeautifulSoup(data.content, "lxml")
            for a in soup.find_all("a", attrs={"data-qa": "vacancy-serp__vacancy-title"}):
                vacancy_link = f"https://hh.ru{a.attrs['href']}"
                vacancy = get_vacancy(vacancy_link)
                if vacancy:
                    vacancies.append(vacancy)
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
        time.sleep(1)
    return vacancies

def get_vacancy(vacancy_link):
    ua = fake_useragent.UserAgent()
    try:
        data = requests.get(
            url=vacancy_link,
            headers={"user-agent": ua.random}
        )
        if data.status_code != 200:
            return
        soup = BeautifulSoup(data.content, "lxml")
        title = soup.find(attrs={"data-qa": "vacancy-title"}).text
        company = soup.find(attrs={"data-qa": "vacancy-company-name"}).text
        salary = soup.find(attrs={"data-qa": "vacancy-salary"}).text
        experience = soup.find(attrs={"data-qa": "vacancy-experience"}).text
        employment_type = soup.find(attrs={"data-qa": "vacancy-employment-type"}).text
        schedule = soup.find(attrs={"data-qa": "vacancy-work-schedule"}).text
        location = soup.find(attrs={"data-qa": "vacancy-view-location"}).text
        tags = [tag.text for tag in soup.find(attrs={"data-qa": "vacancy-serp__vacancy-skills"}).find_all(attrs={"data-qa": "bloko-tag__section_text"})]
        vacancy = {
            "title": title,
            "company": company,
            "salary": salary,
            "experience": experience,
            "employment_type": employment_type,
            "schedule": schedule,
            "location": location,
            "link": vacancy_link,
            "tags": tags
        }
        return vacancy
    except Exception as e:
        print(f"Ошибка при парсинге вакансии: {e}")
        return None

@bot.message_handler(commands=['analytics'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    itembtn1 = types.KeyboardButton('Аналитика')
    markup.add(itembtn1)

@bot.message_handler(func=lambda message: message.text == 'Аналитика')
def get_analytics(message):
    try:
        response = requests.get(ANALYTICS_URL)
        response.raise_for_status()  # Проверка на ошибки HTTP
        data = response.json()

        # Форматируем ответ для Telegram
        text = f"📊 Аналитика по HH.ru:\n" \
               f"  Вакансия: {data['vacancies']}\n" \
               f"  Кандидат: {data['resumes']}\n" \
               f"  Вакансий: {data['vacancy_count']}\n" \
               f"  Кандидатов: {data['candidate_count']}\n" \
               f"  Среднее число кандидатов на вакансию: {data['avg_candidates_per_vacancy']:.2f}"
               
        
                 
                
               
        bot.send_message(message.chat.id, text)

    except requests.exceptions.RequestException as e:
        bot.send_message(message.chat.id, f"Ошибка получения данных: {e}")
bot.polling()