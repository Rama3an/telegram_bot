from telegram.utils.request import *
from telegram import *
from telegram.ext import *
from bot_commands import do_text_errors, get_paper, do_start, do_help, get_favorites
from bot_button_handler import keyboard_callback_handler
from data_base.config import TOKEN


class Bot:
    # Правильное подключение
    request = Request(
        connect_timeout=0.5,
        read_timeout=1.0,
    )
    bot = Bot(
        request=request,
        token=TOKEN,
    )
    # Обработчик
    updater = Updater(
        bot=bot,
        use_context=True,
    )

    message_handler_start = CommandHandler('start', do_start)
    updater.dispatcher.add_handler(message_handler_start)

    message_handler_help = CommandHandler('help', do_help)
    updater.dispatcher.add_handler(message_handler_help)

    message_handler_paper = CommandHandler('paper', get_paper)
    updater.dispatcher.add_handler(message_handler_paper)

    message_handler_favorites = CommandHandler('favorites', get_favorites)
    updater.dispatcher.add_handler(message_handler_favorites)

    message_handler_keyboard = CallbackQueryHandler(callback=keyboard_callback_handler,
                                                    pass_chat_data=True)
    updater.dispatcher.add_handler(message_handler_keyboard)

    message_handler = MessageHandler(Filters.text, do_text_errors)
    updater.dispatcher.add_handler(message_handler)

    # Запустить бесконечную обработку входящих сообщений
    updater.start_polling()
    updater.idle()
