import time
import logging
import mysql.connector
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import configparser
import questions

config = configparser.ConfigParser()
config.read('config/config.ini')
TOKEN = config['TELEGRAM']['bot-token']


bot = Bot(TOKEN)

# For example use simple MemoryStorage for Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

db_config = {
  'user': config['MYSQL']['user'],
  'password': config['MYSQL']['password'],
  'host': config['MYSQL']['host'],
  'database': config['MYSQL']['database'],
  'raise_on_warnings': True
}

mydb = mysql.connector.connect(**db_config)

mycursor = mydb.cursor()

form_library = questions.load_form_lib('forms')


async def mess_handler(message: types.Message, raw_state: str, state: FSMContext):
    print('handler_starteddd!!!')
    print(raw_state)
    # searching for state
    for frm in form_library:
        found_questions = [q for q in frm.questions if q.state.state == raw_state]
        if len(found_questions) == 0:
            continue  # not found
        # found searching question by state
        async with state.proxy() as data:
            data[found_questions[0].id] = message.text
        next_q = [q for q in frm.questions if q.id == found_questions[0].next_id]
        if len(next_q) != 0:
            # asking next question
            await next_q[0].state.set()
            await message.answer(next_q[0].text)
        else:
            # last question
            await State.set(State())
            params = (message.from_user.id,)

            async with state.proxy() as data:
                for q in frm.questions:
                    params = params + (data[q.id],)

                mycursor.execute("CALL setPlayer (%s,%s,%s,%s)",
                                     params)
                mydb.commit()
            print('last question reached. Data saved.')
        print("form:" + str(frm.__dict__) )


async def command_handler(message: types.Message):
    # searching for a form to start
    cur_form = [frm for frm in form_library if '/' + frm.command == message.text][0]
    # explaining the form.
    await message.reply(cur_form.title)
    await message.answer(cur_form.description)
    # asking first question
    await cur_form.questions[0].state.set()
    await message.answer(cur_form.questions[0].text)
    print(f'form "{cur_form.id}" started.')


for form in form_library:
    form.fill_states()
    dp.register_message_handler(mess_handler, state=form.state_group)
    dp.register_message_handler(command_handler, commands=form.command)


@dp.message_handler(state='*', commands=['list'])
async def list_players(message: types.Message):
    mycursor.execute("SELECT * FROM player")
    result = mycursor.fetchall()
    await message.answer(str(result))


async def setup_bot_commands(param):
    bot_commands = [types.BotCommand(command="/"+frm.command, description=frm.title) for frm in form_library]
    bot_commands.append(types.BotCommand(command="/start", description="Початкове привітання"))
    await bot.set_my_commands(bot_commands)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=setup_bot_commands)
