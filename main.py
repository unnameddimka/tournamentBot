import time
import logging
import mysql.connector
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import configparser

config = configparser.ConfigParser()
config.read('config/config.ini')
TOKEN = config['TELEGRAM']['bot-token']


bot = Bot(TOKEN)

# For example use simple MemoryStorage for Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

config = {
  'user': config['MYSQL']['user'],
  'password': config['MYSQL']['password'],
  'host': config['MYSQL']['host'],
  'database': config['MYSQL']['database'],
  'raise_on_warnings': True
}

mydb = mysql.connector.connect(**config)

mycursor = mydb.cursor()

# States
class Form(StatesGroup):
    name = State()  # Will be represented in storage as 'Form:name'
    country = State()  # Will be represented in storage as 'Form:age'
    rank = State()  # Will be represented in storage as 'Form:rank'
    save = State()  # saving data


@dp.message_handler(state='*', commands=['register'])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    logging.info(f"{user_id}:{user_full_name} {time.asctime()}")
    # Set state
    await Form.name.set()
    await message.reply("Реєстрація у системі\n"
                        "Поки що бот тільки збирає інформацію.\n"
                        "Надана інформація використовуватиметься з тестовую метою та не буде росповсюджена.")
    await message.answer("Введіть ваше ім'я.")


@dp.message_handler(state='*', commands=['start'])
async def start_handler(message: types.Message):

    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    logging.info(f"{user_id}:{user_full_name} {time.asctime()}")
    await message.reply("Цей бот коли небудь у чудовій квітучій Україні майбутнього буде працювати з гравцями в ґо та "
                        "проводити турніри. \nСлава Україні! ")


@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    """
    Process user name
    """
    async with state.proxy() as data:
        data['name'] = message.text

    await Form.next()
    await message.answer("З якої ви країни?")


@dp.message_handler(state=Form.country)
async def process_name(message: types.Message, state: FSMContext):
    """
    Process user country
    """
    async with state.proxy() as data:
        data['country'] = message.text
    await Form.next()
    await message.answer("Який ваш ранг? (наприклад 10k, 4d, 9p)")


@dp.message_handler(state=Form.rank)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['rank'] = message.text
        await message.answer(f"Дякую. Про вас зібрані наступні дані {data.values()}")
        mycursor.execute("CALL setPlayer (%s,%s,%s,%s)",
                         (message.from_user.id,
                          data['name'],
                          data['country'],
                          data['rank']
                          ))
        mydb.commit()


@dp.message_handler(state='*', commands=['list'])
async def list_players(message: types.Message):
    mycursor.execute("SELECT * FROM player")
    result = mycursor.fetchall()
    await message.answer(str(result))


async def setup_bot_commands(param):
    bot_commands = [
        types.BotCommand(command="/start", description="Початкове привітання"),
        types.BotCommand(command="/register", description="Реєстрація козака"),
    ]
    await bot.set_my_commands(bot_commands)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=setup_bot_commands)
