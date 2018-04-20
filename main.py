#!/usr/bin/env python
# -*- coding: utf-8 -*-


import telebot
import requests
import json
import numpy as np
from datetime import date, timedelta,datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as pyplot

import threading
# import pickle
import time

# requests.get("http://159.49.112.87/")


TOKEN = '541416193:AAHpVF1yGc8UiiXz0l-iANxWSgOqGpHPR90'

bot = telebot.TeleBot(TOKEN)

markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
# functions = ['/GetTemperatureStatus','/DectiveKeyboardOptions','/GetMoisureStatus','/ActiveKeyboardOptions','/GetMoisureStatus','/ProcessAllData', '/GetGraphics']
functions = ['/DectiveKeyboardOptions','/ActiveKeyboardOptions','/ProcessAllData', '/GetGraphics','/unsubcribe','/subcribe']


# itembtn1 = telebot.types.KeyboardButton('/GetMoisureStatusa')
itembtn2 = telebot.types.KeyboardButton('/DectiveKeyboardOptions')
# itembtn3 = telebot.types.KeyboardButton('/GetTemperatureStatus')
# itembtn4 = telebot.types.KeyboardButton('/GetMoisureStatus')
itembtn5 = telebot.types.KeyboardButton('/ProcessAllData')
itembtn6 = telebot.types.KeyboardButton('/GetGraphics')
itembtn7 = telebot.types.KeyboardButton('/unsubcribe')
itembtn8 = telebot.types.KeyboardButton('/subcribe')
markup.add(itembtn2, itembtn5, itembtn6,itembtn7,itembtn8)
# markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6)
markupHide = telebot.types.ForceReply(selective=False)

init_text = "Hi.\n It's the functions that you can use."
for x in functions:
    init_text += "\n"+"\t"*4+x

subcribe = {}
# try:
# 	with open("idchats.txt", 'rb') as fichero:
# 	    subcribe = pickle.load(fichero)
# except Exception as e:
# 	with open("idchats.txt", 'wb') as fichero:
# 		pickle.dump(subcribe, fichero,0)

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
    pyplot.plot(x, y)
    pyplot.title(str('Sensor : ' + str(data[0]['id'])))
    # pyplot.show()
    pyplot.xticks(rotation=90)
    pyplot.savefig('/tmp/photo.png')
    pyplot.close()
    with open('/tmp/photo.png', 'rb') as photo:
        bot.send_photo(message.from_user.id, photo)

def processData():
    # Get ids sensors
    try:
        sensors = json.loads(requests.get("http://158.49.112.87:8080/", timeout=1).text)
    except Exception as e:
        for id, s in subcribe.iteritems():
            if s is True:
                bot.send_message(id, "Error Servidor Api Caida")
        print e
        return
    # sensors = [{'id':1}, {"id":2}, {"id":3}]
    average = {}
    lastValue = {}
    for sensor in sensors:
        acum = 0
        if sensor["id"] in [1, 2, 3, 4]:    # Procesar Sensores Jardin
            try:
                data = json.loads(requests.get("http://158.49.112.87:8080/" + str(sensor["id"]), timeout=1).text)
            except Exception as e:
                for id, s in subcribe.iteritems():
                    if s is True:
                        bot.send_message(id, "Error Servidor Api Caida")
                print e
                return
            for d in data:
                acum += d["valor"]
            average[sensor["id"]] = acum/len(data)
            lastValue[sensor["id"]] = data[-1]
        else:                            # Procesar AEMET
            pass
    text = ""
    for sensor in sensors:
        if sensor["id"] in [1, 2, 3, 4]:
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
    subcribe[message.from_user.id] = True
    print subcribe
    # with open("idchats.txt", 'wb') as fichero:
    #     pickle.dump(subcribe, fichero, 0)
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
    try:
        sensors = json.loads(requests.get("http://158.49.112.87:8080/", timeout=1).text)
    except Exception as e:
        for id, s in subcribe.iteritems():
            if s is True:
                bot.send_message(id, "Error Servidor Api Caida")
        print e
        return
    for sensor in sensors:
        if sensor["id"] in [1, 2, 3, 4]:  # Procesar Sensores Jardin
            try:
                data = json.loads(requests.get("http://158.49.112.87:8080/" + str(sensor["id"]), timeout=1).text)
            except Exception as e:
                for id, s in subcribe.iteritems():
                    if s is True:
                        bot.send_message(id, "Error Servidor Api Caida")
                print e
                return
            processDataAndSendGraphics(data, message)
        else:  # Procesar AEMET
            pass



@bot.message_handler(commands=['ActiveKeyboardOptions'])
def handle_start_help(message):
    bot.reply_to(message, "ActiveKeyboard", reply_markup=markup)

@bot.message_handler(commands=['DectiveKeyboardOptions'])
def handle_start_help(message):
    bot.reply_to(message, "DectiveKeyboard", reply_markup=markupHide)

@bot.message_handler(commands=['unsubcribe'])
def handle_unsubcribe(message):
	subcribe[message.from_user.id]=False
	# with open("idchats.txt", 'wb') as fichero:
	# 	pickle.dump(subcribe, fichero,0)

@bot.message_handler(commands=['subcribe'])
def handle_subcribe(message):
	subcribe[message.from_user.id]=True
	# with open("idchats.txt", 'wb') as fichero:
	# 	pickle.dump(subcribe, fichero,0)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "I don't know what you mean.\n" + init_text)



def theSystemHasErrors():
    print "comprobando Sistema"
    try:
        sensors = json.loads(requests.get("http://158.49.112.87:8080/", timeout=1).text)
    except Exception as e:
        for id, s in subcribe.iteritems():
            if s is True:
                bot.send_message(id, "Error Servidor Api Caida")
        print e
        return
    for sensor in sensors:
        if sensor["id"] in [1, 2, 3, 4]:  # Procesar Sensores Jardin
            data = json.loads(requests.get("http://158.49.112.87:8080/" + str(sensor["id"]), timeout=1).text)
            list_days=[]
            for d in data:
                f = d['fecha'].split(",")[1].replace(" GMT","")[1:]
                d = datetime.strptime(f, "%d %b %Y %H:%M:%S")
                list_days.append(d)
            last_date = max(list_days)
            now = datetime.now()
            if now + timedelta(minutes = -15)>last_date:
                for id, s in subcribe.iteritems():
                    if s is True:
                        bot.send_message(id, "Error en el sensor: " + str(data[0]['id']))
        else:  # Procesar AEMET
            pass


def worker(bot):
    bot.polling()

t = threading.Thread(target=worker, args=(bot,))
t.start()

# bot.polling()
if __name__ == '__main__':
    while True:
        theSystemHasErrors()
        time.sleep(3*60)
