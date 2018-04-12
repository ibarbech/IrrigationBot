#!/usr/bin/env python
# -*- coding: utf-8 -*-


import telebot
import requests
import json
import numpy as np
from datetime import date, timedelta,datetime
import matplotlib.pyplot as plt

# requests.get("http://159.49.112.87/")


TOKEN = '541416193:AAHpVF1yGc8UiiXz0l-iANxWSgOqGpHPR90'

bot = telebot.TeleBot(TOKEN)

markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
functions = ['/GetTemperatureStatus','/DectiveKeyboardOptions','/GetMoisureStatus','/ActiveKeyboardOptions','/GetMoisureStatus','/ProcessAllData', '/GetGraphics']
# for x in functions:
#     itembtn1 = telebot.types.KeyboardButton(x)
#     markup.add(itembtn1)
itembtn1 = telebot.types.KeyboardButton('/GetMoisureStatusa')
itembtn2 = telebot.types.KeyboardButton('/DectiveKeyboardOptions')
itembtn3 = telebot.types.KeyboardButton('/GetTemperatureStatus')
itembtn4 = telebot.types.KeyboardButton('/GetMoisureStatus')
itembtn5 = telebot.types.KeyboardButton('/ProcessAllData')
itembtn6 = telebot.types.KeyboardButton('/GetGraphics')

markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6)
markupHide = telebot.types.ForceReply(selective=False)

init_text = "Hi.\n It's the functions that you can use."
for x in functions:
    init_text += "\n\t"+x

Tipo2Text ={ "1": "Temperatura ambiente",
             "2": "Humedad ambiente",
             "3": "Humedad de la tierra",
             "4": "Luminosidad",
             "5": "AEMET Fecha de actualización",
             "6": "AEMET Localidad",
             "7": "AEMET Provincia",
             "8": "AEMET Temperatura máxima",
             "9": "AEMET Temperatura mínima",
             "10": "AEMET Estado del cielo",
             "11": "AEMET Cota de nieve",
             "12": "AEMET Viento",
             "13": "AEMET Racha",
             "14": "AEMET Temperatura horas",
             "15": "AEMET Sensación térmica máxima",
             "16": "AEMET Sensación térmica mínima",
             "17": "AEMET Sensación térmica",
             "18": "AEMET Humedad",
             "19": "AEMET Humedad máxima",
             "20": "AEMET Humedad mínima",
             "21": "AEMET Temperatura máxima"
             }

def monthToNum(shortMonth):

    return{
        'Jan' : '01',
        'Feb' : '02',
        'Mar' : '03',
        'Apr' : '04',
        'May' : '05',
        'Jun' : '06',
        'Jul' : '07',
        'Aug' : '08',
        'Sep' : '09',
        'Oct' : '10',
        'Nov' : '11',
        'Dec' : '12'
}[shortMonth]

def processDataAndSendGraphics(data, message):
    dictDays = {}
    for dato in data:
        f = dato["fecha"].replace(",", "").split(" ")
        d = str(f[3] + "-" + monthToNum(f[2]) + "-" + f[1])
        if d not in dictDays.keys():
            dictDays[d] = []
        else:
            dictDays[d].append(dato["valor"])
    for k, v in dictDays.iteritems():
        dictDays[k] = np.mean(v)
    listDates=[datetime.strptime(x, "%Y-%m-%d").date() for x in dictDays.keys()]
    d1 = min(listDates)
    d2 = max(listDates)
    delta = d2 - d1
    for i in range(delta.days+1):
        d = (d1 + timedelta(days=i)).__str__()
        if d not in dictDays.keys():
            dictDays[d] = 0
    lists = sorted(dictDays.items())  # sorted by key, return a list of tuples
    x, y = zip(*lists)  # unpack a list of pairs into two tuples
    plt.plot(x, y)
    plt.title(str('Sensor : ' + str(data[0]['id'])))
    # plt.show()
    plt.xticks(rotation=90)
    plt.savefig('/tmp/photo.png')
    plt.close()
    with open('/tmp/photo.png', 'rb') as photo:
        bot.send_photo(message.from_user.id, photo)

def processData():
    # Get ids sensors
    sensors = json.loads(requests.get("http://158.49.112.87:8080/").text)
    # sensors = [{'id':1}, {"id":2}, {"id":3}]
    average = {}
    lastValue = {}
    for sensor in sensors:
        acum = 0
        if sensor["id"] in [1, 2, 3, 4]:    # Procesar Sensores Jardin
            data = json.loads(requests.get("http://158.49.112.87:8080/" + str(sensor["id"])).text)
            for d in data:
                acum += d["valor"]
            average[sensor["id"]] = acum/len(data)
            lastValue[sensor["id"]] = data[-1]
        else:                            # Procesar AEMET
            pass
    text = ""
    for sensor in sensors:
        text += Tipo2Text[str(sensor["id"])] + "\n"
        text += "\t\t\tValor Medio: " + str(average[sensor["id"]]) + "\n"
        text += "\t\t\tUltimo Valor tomado:" + "\n"
        text += "\t\t\t\t\tFecha:" + str(lastValue[sensor["id"]]["fecha"]) + "\n"
        # text += "\t\t\t\t\tid   :" + str(lastValue[sensor["id"]]["id"]) + "\n"
        # text += "\t\t\t\t\ttipo :" + str(lastValue[sensor["id"]]["tipo"]) + "\n"
        text += "\t\t\t\t\tValor:" + str(lastValue[sensor["id"]]["valor"]) + "\n"
    return text

@bot.message_handler(commands=['start','help'])
def handle_start_help(message):
    bot.reply_to(message, init_text)


@bot.message_handler(commands=['GetTemperatureStatus'])
def handle_start_help(message):
    bot.reply_to(message, "Falta implementar")



@bot.message_handler(commands=['GetMoisureStatus'])
def handle_start_help(message):
    bot.reply_to(message, "Falta implementar")

@bot.message_handler(commands=['ProcessAllData'])
def handle_start_help(message):
    bot.reply_to(message, processData(), reply_markup=markupHide)

@bot.message_handler(commands=['GetGraphics'])
def handle_start_help(message):
    # Get ids sensors
    sensors = json.loads(requests.get("http://158.49.112.87:8080/").text)
    for sensor in sensors:
        if sensor["id"] in [1, 2, 3, 4]:  # Procesar Sensores Jardin
            data = json.loads(requests.get("http://158.49.112.87:8080/" + str(sensor["id"])).text)
            processDataAndSendGraphics(data, message)
        else:  # Procesar AEMET
            pass



@bot.message_handler(commands=['ActiveKeyboardOptions'])
def handle_start_help(message):
    bot.reply_to(message, "ActiveKeyboard", reply_markup=markup)

@bot.message_handler(commands=['DectiveKeyboardOptions'])
def handle_start_help(message):
    bot.reply_to(message, "DectiveKeyboard", reply_markup=markupHide)



@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, "I don't know what you mean.\n" + init_text)

bot.polling()
