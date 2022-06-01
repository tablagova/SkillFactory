import telebot
from config import currencies, TOKEN
from extentions import ConversionException, CryptoConverter

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def repeat(message: telebot.types.Message):
    text = 'Введите команду боту в следующем формате:\n<имя валюты> <в какую валюту перевести> ' \
           '<количество переводимой валюты>'
    bot.reply_to(message, text)
    text = "Получить список доступных валют: /values"
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = 'Доступные валюты:\n' + '\n'.join(list(currencies.keys()))
    bot.reply_to(message, text)


@bot.message_handler(content_types=['text'])
def confirm(message: telebot.types.Message):
    try:
        values = message.text.split()

        if len(values) > 3:
            raise ConversionException('Слишком много параметров')
        elif len(values) < 3:
            raise ConversionException('Слишком мало параметров')
        base, quote, amount = values
        total = CryptoConverter.get_price(base, quote, amount)

    except ConversionException as e:
        bot.reply_to(message, f'Ошибка запроса. \n{e}')
    except Exception as e:
        bot.reply_to(message, f'Не удалось обработать команду\n {e}')
    else:
        bot.send_message(message.chat.id, f'Цена {amount} {base} в {quote} - {total} {currencies[quote]["symbol"].upper()}')


bot.polling(none_stop=True)
