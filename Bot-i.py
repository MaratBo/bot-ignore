# -*- coding: utf-8 -*-
import telebot
from telebot import types
from time import sleep
import psycopg2
from configparser import ConfigParser
import datetime

config = ConfigParser()
config.read('config.ini')
bot = telebot.TeleBot('1270584450:AAGAUIUxlBzOBOzWWkCREkDNHlV3SQUHoqo')
keyboard = telebot.types.ReplyKeyboardMarkup(True)
keyboard.row('ЦФО', 'Города', 'Рязань')
keyboard2 = types.InlineKeyboardMarkup(True)

kod = {'tulskaya_oblast':'TLA',
          'smolenskaya_oblast':'SML',
          'yaroslavskaya_oblast':'YVL',
          'voronezhskaya_oblast':'VRNJ',
          'nizhegorodskaya_oblast':'NNV',
          'ryazanskaya_oblast':'RZN'}

HRU = {'tulskaya_oblast':'Тула',
          'smolenskaya_oblast':'Смоленск',
          'yaroslavskaya_oblast':'Ярославль',
          'voronezhskaya_oblast':'Воронеж',
          'nizhegorodskaya_oblast':'Н.Новгород',
          'ryazanskaya_oblast':'Рязань'}

conn = psycopg2.connect(database=config['DEFAULT']['database'],
                        user=config['DEFAULT']['username'],
                        password=config['DEFAULT']['password'],
                        host=config['DEFAULT']['host'], port = "5432")
mydb = conn.cursor()

def comtrance():
    #return 'чуть позже..'
    mydb.execute('select * from comtrance')
    z = mydb.fetchall()
    k = list(z[-1])
    info = (k[0] + '\n' +
            'Москва - ' + str(k[1]) + ' / ' + str(k[2]) + '\n' +
            'Питер - ' + str(k[3]) + ' / ' + str(k[4]) + '\n' +
            'Россия - ' + str(k[5]) + ' / ' + str(k[6]))
    return info

time = datetime.date.today()
averg = []
CFO_data = []


def seven_days(city):
    mydb.execute("SELECT * from {}".format('CARS_'+city))
    rows = mydb.fetchall()
    av_new = int(sum([x[2] for x in rows[-8:-2]])/len(rows[-8:-2]))
    aru_new = int(sum([x[3] for x in rows[-8:-2]]) / len(rows[-8:-2]))
    av_used = int(sum([x[4] for x in rows[-8:-2]]) / len(rows[-8:-2]))
    aru_used = int(sum([x[5] for x in rows[-8:-2]]) / len(rows[-8:-2]))
    averg.append(av_new)
    averg.append(aru_new)
    averg.append(av_used)
    averg.append(aru_used)
    conn.commit()
    return averg[-4:]


def cfo():
    cities = ['CARS_RZN', 'CARS_SML', 'CARS_TLA', 'CARS_YVL']
    for position in range(2, 6):
        for city in cities:
            mydb.execute("SELECT * from {}".format(city))
            rows = mydb.fetchall()
            CFO_data.append(int(rows[-1][position]))
    data = sum(CFO_data[0:4]), sum(CFO_data[4:8]), sum(CFO_data[8:12]), sum(CFO_data[12:16])
    k = list(data)
    info = ('Статус на ' + str(time) + ', ЦФО' + '\n' +
            'Новые, Avito/Auto.ru - ' + str(k[0]) + ' / ' + str(k[1]) + '\n' +
            'С пробегом, Avito/Auto.ru - ' + str(k[2]) + ' / ' + str(k[3]))
    conn.commit()
    return info


def legkovie(key):
    prev = seven_days(kod[key])
    request = 'select * from CARS_' + kod[key]
    mydb.execute(request)
    z = mydb.fetchall()
    k = list(z[-1])
    info = ('Статус на ' + k[0] + ', ' + HRU[key] + '\n' +
        'Магазинов на Avito - ' + str(k[1]) + '\n' +
        'Новые, Avito/Auto.ru - ' + str(k[2]) + ' / ' + str(k[3]) + '\n' +
        'С пробегом, Avito/Auto.ru - ' + str(k[4]) + ' / ' + str(k[5]) + '\n\n' +
        'Предыдущие 7 дней, среднее:' + '\n' +
        'Новые, Avito/Auto.ru - ' + str(prev[0]) + ' / ' + str(prev[1]) + '\n' +
        'С пробегом, Avito/Auto.ru - ' + str(prev[2]) + ' / ' + str(prev[3]))
    return info


@bot.message_handler(commands=['start'])
def dialog(message):
    sleep(1)
    bot.send_message(message.chat.id, 'Привет! теперь ты можешь запросить данные', reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def send_message(message):
    if message.text == 'Рязань':
        bot.send_message(message.chat.id, legkovie('ryazanskaya_oblast'))

    elif message.text == 'ЦФО':
        bot.send_message(message.chat.id, cfo())

    else:
        tula = types.InlineKeyboardButton(text='Тульская', callback_data='c1')
        keyboard2.add(tula)
        smolensk = types.InlineKeyboardButton(text='Смоленская', callback_data='c2')
        keyboard2.add(smolensk)
        yaroslavl = types.InlineKeyboardButton(text='Ярославская', callback_data='c3')
        keyboard2.add(yaroslavl)
        ryazan = types.InlineKeyboardButton(text='Рязанская', callback_data='c4')
        keyboard2.add(ryazan)
        chelny = types.InlineKeyboardButton(text='Воронежская', callback_data='c5')
        keyboard2.add(chelny)
        nizhniy = types.InlineKeyboardButton(text='Нижегородская', callback_data='c6')
        keyboard2.add(nizhniy)
        bot.send_message(message.from_user.id, 'Выбери область', reply_markup=keyboard2)


@bot.callback_query_handler(func=lambda call:True)
def callback_worker(call):
    if call.data == "c4":
        bot.send_message(call.message.chat.id, legkovie('ryazanskaya_oblast'))
    elif call.data == 'c1':
        bot.send_message(call.message.chat.id, legkovie('tulskaya_oblast'))
    elif call.data == 'c2':
        bot.send_message(call.message.chat.id, legkovie('smolenskaya_oblast'))
    elif call.data == 'c3':
        bot.send_message(call.message.chat.id, legkovie('yaroslavskaya_oblast'))
    elif call.data == 'c5':
        bot.send_message(call.message.chat.id, legkovie('voronezhskaya_oblast'))
    elif call.data == 'c6':
        bot.send_message(call.message.chat.id, legkovie('nizhegorodskaya_oblast'))

bot.polling(none_stop=True, interval=0)


