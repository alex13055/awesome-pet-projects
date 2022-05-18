#!/usr/bin/env python
import telebot
from Weather import Weather
from config import tg_api_key, msg_hist_file
from save_history import save_history, clear_history
import pandas as pd
from datetime import datetime

bot = telebot.TeleBot(tg_api_key)
condition = False

@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(message.chat.id, "Привет! Я могу показать тебе текущую погоду в любом городе.")
    bot.send_message(message.chat.id, "Просто введи /weather, а после - название города ;) ")
    user_requests = get_user_history(message.chat.username)
    if user_requests:
        bot.send_message(message.chat.id, "Еще у меня есть список твоих предыдущих запросов") 
        bot.send_message(message.chat.id, "Если ты хочешь посмотреть историю своих запросов, нажми /history") 

@bot.message_handler(commands=["history"])
def click_show_history(message):
    user_requests = get_user_history(message.chat.username)
    if not user_requests:
        bot.send_message(message.chat.id,"У нас нет истории твоих запросов")
    else:
        bot.send_message(message.chat.id,f"Топ 5 предыдущих запросов: {user_requests}")
        bot.send_message(message.chat.id, "Если вы хотите удалить всю историю своих запросов, нажмите /clear_history") 

@bot.message_handler(commands=["clear_history"])
def click_clear_history(message):
    user_requests = get_user_history(message.chat.username)
    if user_requests:
        clear_history("username", message.chat.username,msg_hist_file)
        bot.send_message(message.chat.id, "История удалена!")
    else:
        bot.send_message(message.chat.id,"У нас нет истории твоих запросов")

@bot.message_handler(commands=["weather"])
def click_weather(message):
    bot.send_message(message.chat.id, "Введи город:")

@bot.message_handler(func= lambda message: True)
def send_weather(message):
    global weather 
    weather = Weather(message.text.strip())
    if not weather.correct_response:
        bot.send_message(message.chat.id, "Вы ввели неверный адрес, пожалуйста повторите попытку")
    else:
        bot.send_message(message.chat.id,f"""
        Сегодня в {weather.city_name} {int(weather.temperature)}°, скорость ветра {int(weather.wind_speed)} м/с, давление {weather.pressure}, погодные условия {weather.condition}, местное время {weather.datetime}""") 
        bot.send_message(message.chat.id,weather.give_advise())
        create_and_save_data(message)

def create_and_save_data(message):
    save_df = pd.DataFrame({
    "message_id": weather.id,    
    "chat_id": message.chat.id,
    "username": message.chat.username,
    "datetime": datetime.fromtimestamp(message.date).isoformat(timespec='minutes'),
    "message": message.text
    }, index = [0])

    save_history(save_df,msg_hist_file)

def get_user_history(username):
    try:
        df = pd.read_csv(msg_hist_file)
        df_username = df[df.username.isin([username])].sort_values(by = "datetime")
    except FileNotFoundError:
        return None
    else:
        if df_username.empty:
            return None
        return list(df_username.message.head())

bot.infinity_polling()