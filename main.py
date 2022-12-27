import requests
import telebot
import shutil

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

        return f"Sell {currency_pair_splitted[0].upper()} price: {sell_price} {currency_pair_splitted[1].upper()}"
    except Exception as ex:
        print(ex)
        return "Something was wrong..."


def telegram_bot(telegram_token):
    bot = telebot.TeleBot(telegram_token)

    @bot.message_handler(commands=["start"])
    def start_message(message):
        bot.send_message(
            message.chat.id,
            "Hello friend!\nThat's what I can:\n"
            "/price_btc - current price of Bitcoin (BTC)\n"
            "/price_eth - current price of Ethereum (ETH)\n"
            "/random_cat - random cat"
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
            res = requests.get(url, stream=True)

            if res.status_code == 200:
                with open(file_temp, 'wb') as f:
                    shutil.copyfileobj(res.raw, f)
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "- Image successfully downloaded:", file_temp)
            else:
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "- Image download error")

            image = open(file_temp, 'rb')

            bot.send_photo(
                message.chat.id,
                image
            )
        except Exception as ex:
            print(ex)
            bot.send_message(
                message.chat.id,
                "Something was wrong..."
            )

    @bot.message_handler(content_types=["text"])
    def send_text(message):
        bot.send_message(
            message.chat.id,
            "What? Check the command!"
        )

    bot.polling()


if __name__ == "__main__":
    telegram_bot(telegram_token)

