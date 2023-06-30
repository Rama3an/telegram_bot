from telegram import *
from telegram.ext import *
from requests import get
import re
from data_base.connection_db import connection
from bot_button_handler import get_add_keyboard, get_delete_keyboard, get_compiled_add_keyboard

BASE_URL = 'http://export.arxiv.org/api/query'


def log_errors(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:

            error_message = f'Произошла ошибка {e}'
            print(error_message)
            raise e

    return inner


@log_errors
def do_text_errors(update: Update, context: CallbackContext):
    update.message.reply_text(
        text="Напишите еще раз, пожалуйста. Я вас не понимаю.",
    )


def get_favorites(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    # проверка на наличие в базе данных сохраненных статей
    with connection.cursor() as cursor:
        select = (f"SELECT * FROM Paper "
                  f"WHERE telegram_id = {chat_id}")
        cursor.execute(select)
        favorites = cursor.fetchall()

    if favorites:
        for i, value in enumerate(favorites):
            update.message.reply_text(
                text=f"{i + 1}. {value.get('paper')}",
                reply_markup=get_delete_keyboard(),
            )
    else:
        update.message.reply_text(text="У Вас пока нет избранных статей :( "
                                       "Как найдете интересную статью –– сразу добавьте!")


@log_errors
def do_start(update: Update, context: CallbackContext):
    message_text = ("Привет! Чтобы воспользоваться ботом Вам нужно написать команду:\n\n"
                    "<b>/paper &lt;имя/фамилия&gt; ключевое слово</b>\n\n"
                    "Пример: <b>&lt;leonid positselski, jan&gt; topology</b>\n\n"
                    "Ключевых слов или же имен авторов может быть несколько.\n\n"
                    "Так же вы можете добавить статьи в избранные и найти их по команде <em>/favorites</em>.\n\n"
                    "Главное соблюдать валидацию запроса и у вас все получится!\n\n"
                    "Если остались вопросы, то вызовите функцию <em>/help</em>, которая все подробно расскажет.\n\n"
                    "Удачи!")

    update.message.reply_html(
        text=message_text,
    )


@log_errors
def do_help(update: Update, context: CallbackContext):
    message_text = ("У бота основной командой является <em>/paper</em>, она дает возможность получать статьи "
                    "в виде ссылки на pdf с сайта arxiv.org.\n"
                    "Чтобы воспользоваться данной командой, надо знать, как она работает.\n\n"
                    "Вот пример: <b>/paper &lt;leonid positselski, jan&gt; topology</b>\n\n"
                    "В таких скобках &lt;&gt; через запятую с пробелом указываются имена и фамилии авторов, "
                    "если они не нужны, то ничего не пишите.\n\n"
                    "После через пробел нужно указать ключевые слова, "
                    "если же вы ищите только по автору, то опять же, не указывайте.\n\n"
                    "Так же можете задать количество статей, которые хотите найти. Изначально их 3.\n"
                    "Для этого в конце укажите, сколько надо статей.\n\n"
                    "Вот так: <b>/paper &lt;leonid positselski, jan&gt; topology 5</b>\n\n"
                    "Можно добавить любимые статьи в избранные.\n"
                    "Для этого надо нажать кнопку добавить под каждой статьей, а чтобы получить к ним доступ, "
                    "нужно воспользоваться командой <em>/favorites</em>.\n\n"
                    "Если хотите удалить статью, то нажмите на соответсвующую кнопку.")
    update.message.reply_html(
        text=message_text,
    )


@log_errors
def get_paper(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    text = update.message.text[7:]
    pattern_autor_and_word = re.findall(r"^<[^<>]+>[^<>]+$", text)
    pattern_autor = re.findall(r"^<[^<>]+>$", text)
    pattern_word = re.findall(r"^[^<>]+$", text)
    if not (pattern_word or pattern_autor or pattern_autor_and_word):
        update.message.reply_text(
            text="В команде есть ошибка! Исправьте и напишите заново :)"
        )
    else:
        autor_list = "".join(re.findall(r"<.+>", update.message.text[6:]))[1:-1]
        autor_message = ""
        if autor_list:
            autor_message = f"au:{' AND au:'.join(autor_list.split(', '))} "
            key_message = update.message.text[update.message.text.index('>') + 1:].split()
        else:
            key_message = update.message.text[6:].split()

        try:
            message_response = " AND all:".join(key_message[:-1])
            max_result = int(key_message[-1])
        except:
            message_response = " AND all:".join(key_message)
            max_result = 3

        if message_response:
            message_response = f"all:{message_response}"

        text_api_response = f"{BASE_URL}?search_query={autor_message}{message_response}&max_results={max_result}"
        response = get(text_api_response)

        atom_response_title = re.findall(r'(<title>[^&=]+</title>)', response.text)
        atom_response_title = '!_!'.join(atom_response_title).replace('<title>', '').replace('</title>', ''). \
            replace('\n ', '').split('!_!')

        atom_response_pdf = re.findall(r'http://arxiv.org/pdf/[^"]+', response.text)
        if atom_response_pdf:

            for i, title_and_pdf in enumerate(list(zip(atom_response_title, atom_response_pdf))):
                result = f"{i + 1}. {title_and_pdf[0]}\n" \
                         f"{(len(str(i))) * ' '}  {title_and_pdf[1]}\n"

                # проверка на наличие записей в бд
                with connection.cursor() as cursor:
                    select = (f"SELECT * FROM Paper "
                              f"WHERE telegram_id = {chat_id} "
                              f"AND paper = '{result[result.index('.') + 2:-1]}'")
                    cursor.execute(select)
                    paper_in_bd = cursor.fetchall()

                if not paper_in_bd:
                    update.message.reply_text(
                        text=result,
                        reply_markup=get_add_keyboard(),
                    )
                else:
                    update.message.reply_text(
                        text=result,
                        reply_markup=get_compiled_add_keyboard(),
                    )
        else:
            update.message.reply_text(
                text="Мы ничего не нашли(. Сожалеем, попробуйте поискать другие интересные статьи :)",
            )
