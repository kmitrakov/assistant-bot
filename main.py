import requests
import telebot
import shutil
import httplib2

from settings import *
from decouple import config
from datetime import datetime
from pprint import pprint

telegram_token = config("telegram_token", default="")
weather_token = config("weather_token", default="")


def get_price(currency_pair):
    request_url = exchange_api_url + currency_pair
    currency_pair_splitted = currency_pair.split("_")

    try:
        req = requests.get(request_url, timeout=3)
        response = req.json()

        sell_price = response[currency_pair]["sell"]

        return f"Цена продажи {currency_pair_splitted[0].upper()}: {sell_price} {currency_pair_splitted[1].upper()}"

    except Exception as ex:
        print(ex)
        return "Что-то пошло не так..."


def get_weather(weather_token):
    request_url = weather_url + weather_token

    try:

        req = requests.get(request_url, timeout=3)
        data = req.json()

        weather = data["weather"][0]["description"].capitalize()
        temperature = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        sunrise = datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset = datetime.fromtimestamp(data["sys"]["sunset"])
        sunrise_time = sunrise.strftime("%H:%M:%S")
        sunset_time = sunset.strftime("%H:%M:%S")
        length_of_the_day = sunset - sunrise

        return f"Погода в Москве ({weather}):\n"\
               f"- Температура: {temperature} C°\n"\
               f"- Влажность: {humidity}%\n"\
               f"- Давление: {pressure} мм\n"\
               f"- Ветер: {wind} м/сек\n"\
               f"- Восход солнца: {sunrise_time}\n"\
               f"- Закат солнца: {sunset_time}\n"\
               f"- Продолжительность дня: {length_of_the_day}"

    except Exception as ex:
        print(ex)
        return "Что-то пошло не так..."


def telegram_bot(telegram_token):
    bot = telebot.TeleBot(telegram_token)

    @bot.message_handler(commands=["start", "help"])
    def start_message(message):
        bot.send_message(
            message.chat.id,
            "Привет, человек!\nВот что я умею:\n"
            "/price_btc - показать текущую цену продажи Bitcoin (BTC)\n"
            "/price_eth - показать текущую цену продажи Ethereum (ETH)\n"
            "/random_cat - показать котика\n"
            "/random_dog - показать пёсика\n"
            "/weather_moscow - показать погоду в Москве\n"
            "/help - показать список команд"
        )

    @bot.message_handler(commands=["price_btc"])
    def price_btc_message(message):
        bot.send_message(
            message.chat.id,
            get_price("btc_usd")
        )

    @bot.message_handler(commands=["price_eth"])
    def price_eth_message(message):
        bot.send_message(
            message.chat.id,
            get_price("eth_usd")
        )

    @bot.message_handler(commands=["random_cat"])
    def random_cat_message(message):
        request_url = random_cat_url
        file_temp = "temp/images/" + datetime.now().strftime("%Y%m%d%H%M%S") + ".jpeg"

        try:
            h = httplib2.Http('.cache')
            response, content = h.request(request_url)
            out = open(file_temp, 'wb')
            out.write(content)
            out.close()

            image = open(file_temp, 'rb')

            bot.send_photo(
                message.chat.id,
                image
            )

        except Exception as ex:
            print(ex)
            bot.send_message(
                message.chat.id,
                "Что-то пошло не так..."
            )

    @bot.message_handler(commands=["random_dog"])
    def random_dog_message(message):
        request_url = random_dog_url
        file_temp = "temp/images/" + datetime.now().strftime("%Y%m%d%H%M%S") + ".jpeg"

        try:
            req = requests.get(request_url, timeout=3)
            data = req.json()

            request_url_1 = data[0]

            h = httplib2.Http('.cache')
            response, content = h.request(request_url_1)
            out = open(file_temp, 'wb')
            out.write(content)
            out.close()

            image = open(file_temp, 'rb')

            bot.send_photo(
                message.chat.id,
                image
            )

        except Exception as ex:
            print(ex)
            bot.send_message(
                message.chat.id,
                "Что-то пошло не так..."
            )

    @bot.message_handler(commands=["weather_moscow"])
    def weather_moscow(message):
        bot.send_message(
            message.chat.id,
            get_weather(weather_token)
        )

    @bot.message_handler(content_types=["text"])
    def send_text(message):
        bot.send_message(
            message.chat.id,
            "Я не знаю такой команды..."
        )

    bot.polling()


if __name__ == "__main__":
    telegram_bot(telegram_token)
    # print(get_weather(weather_token))
