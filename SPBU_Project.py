import bs4
import mysql.connector
import requests
import cryptography
from configparser import ConfigParser
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from bs4 import BeautifulSoup
import getpass
import pymysql
import psycopg2
from mysql.connector import MySQLConnection, Error
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sklearn
import numpy as np
import pandas as pd
import csv
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier

storage = MemoryStorage()

try:
    url = 'https://spbu.ru/postupayushchim/programms/bakalavriat?view=table'
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
except Error as e:
    print(f"The error '{e}' occurred")

Domen = 'https://spbu.ru'
Links = []

answers = [0, 0, 0, 0, 0, 0]
Types = ["по названию", "по коду", "по укрупненной группе"]
df = pd.read_csv('C:/Users/tema2/PycharmProjects/pythonProject/AACh_golland_res_csv1.csv')
df1 = pd.read_csv('C:/Users/tema2/PycharmProjects/pythonProject/AACh_golland_res_csv2.csv')
saved_column = df['res']
saved_column1 = df1['res']
saved_column_ = df['1']
saved_column_1 = df1['1']


result = ["профессии механика, электрика, инженера, агронома, садовода, кондитера, повара и другие профессии, "
          "которые предполагают решение конкретных задач, наличие подвижности, настойчивости, связь с техникой",
          "профессии научно-исследовательского направления: ботаник, физик, философ, программист и другие, "
          "в деятельности которых необходимы творческие способности и нестандартное мышление.",
          "профессии, связанные с обучением, лечением и обслуживанием, требующие постоянного контакта и общения с людьми"
          ", способностей к убеждению.", "профессии бухгалтер, патентовед, нотариус, топограф, корректор и другие, "
          "направленные на обработку информации, предоставленной в виде условных знаков, цифр, формул, текстов.",
          "профессии предприниматель, менеджер, продюсер и другие, связанные с руководством, управлением и "
          "влиянием на разных людей в разных ситуациях.", "профессии, связанные с актерско-сценической, музыкальной, "
          "изобразительной деятельностью."]

class item:
    k = 0

def Clear():
    item.k = 0
    answers = [0, 0, 0, 0, 0, 0]


class Navigation(StatesGroup):
    wait_for_type = State()
    wait_for_answer = State()
    wait_for_continue = State()


def read_db_config(filename, section):
    #a function for connection to database and Tg-bot
    parser = ConfigParser()
    parser.read(filename)
    db = []
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db.append(str(item[1]))
    else:
        raise Exception('{0} not found in the {1} file'.format(section, filename))
    return db

config = read_db_config('config.ini', 'database')

try:
    connection = psycopg2.connect(
        database=config[0],
        user=config[1],
        password=config[2],
        host=config[3],
        port=config[4]
    )
    print("Connection to DB successful")
except Error as e:
    print(f"The error '{e}' occurred")

Token = read_db_config('config.ini', 'bot')[0]
bot = Bot(token=Token)
dp = Dispatcher(bot, storage=storage)


def MasFromDB(string):
    # making a list from information that is brought from database
    with connection.cursor() as cursor:
        cursor.execute("select "+string+" from Test;")
        mas = cursor.fetchall()
        mas1 = []
        for i in range(len(mas)):
            mas1.append(StrReplace(str(mas[i])))
    return mas1


def print_edu(text, Type):
    # a function for beautiful output in Tg-bot
    res = ""
    cur = connection.cursor()
    if Type == "по названию":
        cur.execute("select block_name, edu_name, code, level_name, duration_name, number_of_places, description, link "
                    "from levels as l, durations as d, blocks as b, edus as e "
                    "where l.level_id = e.level_id and d.duration_id = e.duration_id and b.block_id = e.block_id "
                    "and edu_name = %(t)s;", {'t': text})
        information = cur.fetchone()
        if len(information) == 0:
            res += "Извините, но такой образовательной программы нет."
        else:
            res = '[' + information[1] + ']' + '(' + information[7] + ')' + '\n' + '\n'
            res += "*Код программы: *" + information[2] + '\n' + '\n'
            res += "*Длительность: *" + information[4]  + '\n' + '\n'
            res += "*Количество бюджетных мест: *" + str(information[5]) + '\n' + '\n'
            res += "*Описание: *" + '\n' + information[6]
        return res
    elif Type == "по коду":
        cur.execute("select edu_name, level_name, duration_name, number_of_places, link "
                    "from levels as l, durations as d, edus as e "
                    "where l.level_id = e.level_id and d.duration_id = e.duration_id "
                    "and code = %(t)s;", {'t': text})
        edus = cur.fetchall()
        if len(edus)==0:
            res += "Извините, но такого кода не найдено."
        else:
            res = "По коду " + text + " найдено:" + '\n'
            for i in range(len(edus)):
                res += str(i+1) + ". " + '[' + edus[i][0] + ']' + '(' + edus[i][4] + ')' + '\n'
                res += "     " + "Уровень обучения: " + edus[i][1] + '\n'
                res += "     " + "Продолжительность: " + edus[i][2] + '\n'
                res += "     " + "Количество бюджетных мест: " + str(edus[i][3]) + '\n'
        return res
    elif Type == "по укрупненной группе":
        cur.execute("select code, edu_name, link "
                    "from levels as l, durations as d, edus as e, blocks as b "
                    "where l.level_id = e.level_id and d.duration_id = e.duration_id and b.block_id = e.block_id "
                    "and block_name = %(t)s;", {'t': text})
        edus = cur.fetchall()
        if len(edus) == 0:
            res += "Извините, но такого блока не найдено."
        else:
            res += "По группе " + text + " найдено:" + '\n'
            for i in range(len(edus)):
                res += "*" + str(i+1) + "*" + ". " + edus[i][0] + " " + '[' + edus[i][1] + ']' + '(' + \
                       edus[i][2] + ')' + '\n'
        return res

def GetProfessionID(prof):
    # the function shows Golland's test logic: when a person chooses a
    # profession, we get the type of it and add 1 to the position type-1
    # in list with answers
    if prof in MasFromDB("Profession1"):
        with connection.cursor() as cursor:
            cursor.execute("select ID1 from Test where Profession1 = %s",(prof))
            ind = cursor.fetchone()
    elif prof in MasFromDB("Profession2"):
        with connection.cursor() as cursor:
            cursor.execute("select ID2 from Test where Profession2 = %s",(prof))
            ind = cursor.fetchone()
    answers[int(StrReplace(str(ind)))-1]+=1 


@dp.message_handler(commands='start' or "Start")
async def Buttons(msg: types.Message):
    # a function, that shows welcome message and outputs all needed buttons
    if item.k != 0:
        Clear()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Функции бота", "Навигация", "Профориентация"]
    keyboard.add(*buttons)
    await msg.answer('Здравствуйте! Я бот СпбГУ. Чем могу быть полезен?', reply_markup=keyboard)


@dp.message_handler(lambda msg:msg.text == "Профориентация")
async def Prof(msg: types.Message):
    # a function for Golland's test
    if item.k != 0:
        Clear()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Функции бота", "Навигация", "Профориентация"]
    keyboard.add(*buttons)
    await msg.answer("Сейчас Вам будет предложен тест, состоящий из 42 вопросов. На каждом этапе будет "
                     "предложена пара профессий, из которой нужно выбрать ту, что больше нравится, "
                     "и нажать на соответсвующую ей кнопку.")
    await msg.answer("Для того, чтобы начать тест, введите команду /test.", reply_markup=keyboard)


@dp.message_handler(lambda msg:msg.text == "Навигация")
async def navigation(msg: types.Message):
    # function for navigation. Here a user have to choose what type of navigation he needs.
    # After clicking a button with type, state machine remembers the answer and goes to the chosentype def
    if item.k != 0:
        Clear()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["по названию", "по коду", "по укрупненной группе"]
    keyboard.add(*buttons)
    await msg.answer("Пожалуйста, выберите тип навигации:", reply_markup=keyboard)
    await Navigation.wait_for_type.set()

async def chosentype(msg: types.Message, state: FSMContext):
    # Here a user gets a suitable answer. Then he can
    if msg.text in Types:
        await state.update_data(navitype=msg.text)
        data = await state.get_data()
        await Navigation.next()
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("Физико-математические, компьютерные и информационные науки", "Естественные науки", "Науки об "
        "обществе", "Гуманитарные науки", "Искусство и культура", "Физическая культура")
        if data['navitype'] == Types[0]:
            await msg.answer("Введите название образовательной программы.")
        elif data["navitype"] == Types[1]:
            await msg.answer("Введите код образовательной программы.")
        else:
            await msg.answer("Выберите название укрупненной группы.", reply_markup=keyboard)

async def NavigationByType(msg: types.Message, state: FSMContext):
    #returns the result of navigation
    await state.update_data(Info=msg.text)
    data = await state.get_data()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Функции бота", "Навигация", "Профориентация"]
    keyboard.add(*buttons)
    if data['navitype'] == Types[0]:
        await msg.answer(print_edu(str(data["Info"]), str(data["navitype"])),
                         parse_mode='Markdown', reply_markup=keyboard)
        await state.finish()
    elif data['navitype'] == Types[1]:
        await msg.answer(print_edu(str(data["Info"]), str(data["navitype"])),
                         parse_mode='Markdown', reply_markup=keyboard)
        await state.finish()
    elif data['navitype'] == Types[2]:
        await msg.answer(print_edu(str(data["Info"]), str(data["navitype"])),
                         parse_mode='Markdown', reply_markup=keyboard)
        await Navigation.next()
        await msg.answer("Если Вы хотите узнать подробную информацию по образовательной программе, то введите "
                         "её название, иначе введите Выход")

async def Continuation(msg: types.Message, state: FSMContext):
    #if user chose navigation by block, he can write edu name and get information about it
    await state.update_data(Answer=msg.text)
    data = await state.get_data()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Функции бота", "Навигация", "Профориентация"]
    keyboard.add(*buttons)
    if data["Answer"] == "Выход":
        await state.finish()
        await msg.answer("Чем я могу быть полезен?", reply_markup=keyboard)
    else:
        await msg.answer(print_edu(str(data["Answer"]), "по названию"),
                         parse_mode='Markdown', reply_markup=keyboard)
        await state.finish()

def PredictEdu():
    #the function for classifier
    result_mas = [[]]
    for j in range(len(saved_column)):
        mas = saved_column[j][1:][:-1].split(', ')
        ar = []
        for i in range(len(mas)):
            ar.append(int(mas[i][5:]))
        result_mas.append(ar)

    #result_mas.remove(ar[0])

    for j in range(len(saved_column1)):
        mas1 = saved_column1[j][1:][:-1].split(', ')
        ar = []
        for i in range(len(mas1)):
            ar.append(int(mas1[i][5:]))
        result_mas.append(ar)

    edus = []

    for j in range(len(saved_column_)):
        edu = ((saved_column_[j].split('"content": ')[1]).split(' "description":')[0])[:-1].replace('"', '')
        edus.append(edu)

    for k in range(len(saved_column_1)):
        edu = ((saved_column_1[k].split('"content": ')[1]).split(' "description":')[0])[:-1].replace('"', '')
        edus.append(edu)

    X = np.array(result_mas)
    Y = np.array(edus)
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.025)

    scaler = StandardScaler()
    scaler.fit(X_train)

    X_train = scaler.transform(X_train)

    classifier = KNeighborsClassifier(n_neighbors=1)
    classifier.fit(X_train, Y_train)
    ans = np.array(answers)
    y_pred = classifier.predict([ans])
    edu = str(y_pred)[2:][:-2]
    print(edu)
    e = "'Технологии программирования'"
    with connection.cursor() as cur:
        if("Технологии программирования" in edu):
            cur.execute('select Block from edus where Name = %s',(e))
            block = cur.fetchone()
        else:
            cur.execute("select Block from edus where Name = %s",("'"+edu[9:]+"'"))
            block = cur.fetchone()
    return StrReplace(str(block))


@dp.message_handler(lambda msg: msg.text == "Функции бота")
async def functions(msg: types.Message):
    #shows Tg-bot's functions to a user
    if item.k != 0:
        Clear()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Функции бота", "Навигация", "Профориентация"]
    keyboard.add(*buttons)
    if "Функции бота" in msg.text:
        await msg.answer(
            "Для старта введите команду /start" + '\n' + '\n' +
            "Если Вы хотите узнать подробную информацию об образовательной программе, нажмите на кнопку *Навигация "
            "по программам*" + '\n' + '\n' + "Для того, чтобы пройти профориентационный "
            "тест, введите нажмите на кнопку *Профориентация*"
            , parse_mode='Markdown', reply_markup=keyboard)


@dp.message_handler()
async def Test(msg: types.Message):
    #Golland's test for a user
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if "test" in msg.text and item.k != 0:
        Clear()
    if ("test" or "start" or "Start" or "Функции бота" or "Навигация" or "Профориентация") not in msg.text and item.k==0:
        await msg.answer("Извините, но я Вас не понимаю. Если Вы хотите узнать, что я умею, введите " + '"Функции бота"')
    elif (("test" in msg.text) or (msg.text in MasFromDB("Profession1")) or (msg.text in MasFromDB("Profession2"))) and \
            item.k < len(MasFromDB("Profession1")):
        i = item.k
        if i != 0:
            GetProfessionID(msg.text)
        keyboard.add(str(MasFromDB("Profession1")[i]), str(MasFromDB("Profession2")[i]))
        item.k += 1
        await msg.answer(str(MasFromDB("Profession1")[i]) + " или " + str(MasFromDB("Profession2")[i]) + "?",
                         reply_markup=keyboard)
    elif item.k != 0 and ((msg.text not in MasFromDB("Profession1")) or (msg.text not in MasFromDB("Profession2"))) and \
            item.k < len(MasFromDB("Profession1")):
        await msg.answer("Пожалуйста, введите одну из предложенных профессий.")
    else:
        if item.k == len(MasFromDB("Profession1")):
            GetProfessionID(msg.text)
            keyboard.add("Функции бота", "Навигация по программам", "Профориентация")
            s = str(PredictEdu())
            await msg.answer("Спасибо Вам за прохождение теста!" + '\n' + '\n'
                             + "По результатам профориентационного " + "тестирования, Вам подходят " +
                             result[answers.index(max(answers))] +'\n' + '\n' + "Возможно, Вам " +
                            "стоит рассмотреть следующий блок направлений: " + s , reply_markup=keyboard)




dp.register_message_handler(Prof, lambda msg: msg.text == "Профориентация")
dp.register_message_handler(navigation, lambda msg: msg.text == "Навигация", state="*")
dp.register_message_handler(chosentype, state=Navigation.wait_for_type)
dp.register_message_handler(NavigationByType, state=Navigation.wait_for_answer)
dp.register_message_handler(Continuation, state=Navigation.wait_for_continue)
dp.register_message_handler(functions)
dp.register_message_handler(Test)


def parser():
    cur = connection.cursor()
    Blocks = {"Физико-математические, компьютерные и информационные науки": 0,
              "Естественные науки": 1,
              "Науки об обществе": 2,
              "Гуманитарные науки": 3,
              "Искусство и культура": 4,
              "Физическая культура": 5
              }
    Levels = {"Бакалавриат": 1, "Cпециалитет": 2}
    Durations = {"4": 1, "5": 2, "6": 3}
    table = soup.find('div', class_="table-programs-wrapper g-container")
    counter = 0
    for i in range(6):
        table_block = table.find('div', id='programs-section-'+str(i))
        block = (table_block.find('div', class_ = 'table-programs__title table-programs__title--'+str(i+1))).get_text().replace('\n', '').strip()
        programs = table_block.find_all('a', class_="table__row")
        for program in programs:
            counter += 1
            name = program.find('div', class_='table__cell').get_text().replace('\xa0', ' ')
            level = program.find('div', class_='table__cell table__cell--inline').get_text()
            code = program.find_all('div', class_='table__cell table__cell--inline')[-1].get_text()
            link = Domen + program.get("href")
            program_request = requests.get(link)
            program_soup = bs4.BeautifulSoup(program_request.text, 'html.parser')
            headline = program_soup.find('div', class_="program-headline")
            duration = headline.find_all('p', class_="program-headline__info")[-1].get_text()
            duration = ''.join(i for i in duration if i.isdigit())
            container = program_soup.find('div', class_='g-row')
            numberofplaces = container.find('table',
                                            class_='program-stats__table program-stats__table--small').get_text().replace(
                '\n', '')[:3]
            numberofplaces = ''.join(i for i in numberofplaces if i.isdigit())
            program_description = program_soup.find('div', class_ = 'collapse-items col-xs-12 col-md-8')
            description = ''
            items = program_description.find_all('div', class_='collapse')
            for item in items:
                if "Описание программы" in str(items):
                    if "Описание программы" in item.get_text():

                        description = ''
                        description += item.get_text().replace("Описание программы", '').replace('\n','. ').strip('. ')
                else:
                    if "Преимущества обучения" in item.get_text():
                        description = ''
                        description += item.get_text().replace("Преимущества обучения", '').replace('\n', '. ').strip('. ')
            cur.execute("insert into EDUs (edu_id, block_id, edu_name, code, level_id, duration_id, number_of_places, "
                        "description, link) values (%(count)s, %(block)s, %(name)s, %(code)s, %(level)s, "
                        "%(duration)s, %(num)s, %(description)s, %(link)s)", {"count": counter,
                                                                              "block": Blocks[block], "name": name,
                                                                              "code": code, "level": Levels[level],
                                                                              "duration": Durations[duration],
                                                                              "num": numberofplaces,
                                                                              "description": description, "link": link})
            connection.commit()
            print(f"{name} successfully added.")

#parser()
if __name__ == '__main__':
    executor.start_polling(dp)

connection.close()