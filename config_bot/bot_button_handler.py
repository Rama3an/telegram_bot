from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from data_base.connection_db import connection

CALLBACK_BUTTON_ADD_DB = "callback_button_add"
CALLBACK_BUTTON_DELETE_DB = "callback_button_delete"
CALLBACK_BUTTON_COMPILE_ADD_DB = "callback_button_compile_add"
CALLBACK_BUTTON_COMPILE_DELETE_DB = "callback_button_compile_delete"

TITLES = {
    CALLBACK_BUTTON_ADD_DB: "Добавить в избранное ⭐",
    CALLBACK_BUTTON_DELETE_DB: "Удалить из избранных ❌",
    CALLBACK_BUTTON_COMPILE_ADD_DB: "Добавлено ✅",
    CALLBACK_BUTTON_COMPILE_DELETE_DB: "Удалено ⭕"
}


def get_add_keyboard():
    keyword = [
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_ADD_DB],
                                 callback_data=CALLBACK_BUTTON_ADD_DB)
        ]
    ]
    return InlineKeyboardMarkup(keyword)


def get_delete_keyboard():
    keyword = [
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_DELETE_DB],
                                 callback_data=CALLBACK_BUTTON_DELETE_DB)
        ]
    ]
    return InlineKeyboardMarkup(keyword)


def get_compiled_add_keyboard():
    keyword = [
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_COMPILE_ADD_DB],
                                 callback_data=CALLBACK_BUTTON_COMPILE_ADD_DB)
        ]
    ]
    return InlineKeyboardMarkup(keyword)


def get_compiled_delete_keyboard():
    keyword = [
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_COMPILE_DELETE_DB],
                                 callback_data=CALLBACK_BUTTON_COMPILE_DELETE_DB)
        ]
    ]
    return InlineKeyboardMarkup(keyword)


def keyboard_callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    current_message = update.effective_message.text
    chat_id = update.effective_message.chat_id

    if data == CALLBACK_BUTTON_ADD_DB:
        # добавление в бд
        with connection.cursor() as cursor:
            insert = (f"INSERT INTO Paper "
                      f"VALUES (NULL, {chat_id}, '{current_message[current_message.index('.') + 2:]}');")
            cursor.execute(insert)
            connection.commit()

        query.edit_message_text(
            text=current_message,
            reply_markup=get_compiled_add_keyboard()
        )
    elif data == CALLBACK_BUTTON_DELETE_DB:

        # Удаление записей и бд
        with connection.cursor() as cursor:
            select = (f"DELETE FROM Paper "
                      f"WHERE telegram_id = {chat_id} AND "
                      f"paper = '{current_message[current_message.index('.') + 2:]}'")
            cursor.execute(select)
            connection.commit()
        query.edit_message_text(
            text=current_message,
            reply_markup=get_compiled_delete_keyboard()
        )
