import requests
import telebot
import shutil
import httplib2

from settings import *
from decouple import config
from datetime import datetime

telegram_token = config("telegram_token", default="")


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
        url = random_cat_url
        file_temp = "temp/images/" + datetime.now().strftime("%Y%m%d%H%M%S") + ".jpeg"

        try:
            h = httplib2.Http('.cache')
            response, content = h.request(url)
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

    @bot.message_handler(content_types=["text"])
    def send_text(message):
        bot.send_message(
            message.chat.id,
            "Я не знаю такой команды..."
        )

    bot.polling()


if __name__ == "__main__":
    telegram_bot(telegram_token)

