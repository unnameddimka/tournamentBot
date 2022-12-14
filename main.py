import time
import logging
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State
import configparser
import questions
import data
import views

config = configparser.ConfigParser()
config.read('config/config.ini')
TOKEN = config['TELEGRAM']['bot-token']


bot = Bot(TOKEN)

# For example use simple MemoryStorage for Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

form_library = questions.load_form_lib('forms')
view_library = views.load_form_lib('data_views')


async def ask_question(message: types.Message, quest: questions.Question, state: FSMContext):
    await quest.state.set()
    await message.answer(quest.text)
    if 'data_view' in quest.__dict__.keys():
        found_views = [frm for frm in view_library if frm.id == quest.data_view]
        if len(found_views) > 0:
            cur_view: views.DataView = found_views[0]
            if 'param_src' in cur_view.__dict__.keys():
                if len(cur_view.param_src) > 0:  # filling parameters
                    cur_view.params = tuple()
                    for src in cur_view.param_src:
                        async with state.proxy() as tg_data:
                            cur_view.params = cur_view.params + (tg_data[src],)
            strs = cur_view.fetch_data()
            await message.answer('\n'.join(strs), parse_mode='HTML')


async def mess_handler(message: types.Message, raw_state: str, state: FSMContext):
    print('handler_starteddd!!!')
    print(raw_state)
    # searching for state
    for frm in form_library:
        found_questions = [q for q in frm.questions if q.state.state == raw_state]
        if len(found_questions) == 0:
            continue  # not found
        # found searching question by state
        async with state.proxy() as tg_data:
            tg_data[found_questions[0].id] = message.text
        next_q = [q for q in frm.questions if q.id == found_questions[0].next_id]
        if len(next_q) != 0:
            # asking next question
            await ask_question(message, next_q[0], state)
        else:
            # last question
            await State.set(State())
            params = (message.from_user.id,)

            async with state.proxy() as tg_data:
                for q in frm.questions:
                    params = params + (tg_data[q.id],)
                data.exec_request(frm.sql_request, params)
            await message.answer(frm.footer)
            print('last question reached. Data saved.')
        print("form:" + str(frm.__dict__))


async def command_handler(message: types.Message, state: FSMContext):
    # searching for a form to start
    found_frms = [frm for frm in form_library if '/' + frm.command == message.text]
    found_views = [frm for frm in view_library if '/' + frm.command == message.text]
    if len(found_frms) > 0:
        cur_form = found_frms[0]
        await message.reply(cur_form.title)
        await message.answer(cur_form.description)
        # asking first question
        await ask_question(message, cur_form.questions[0], state)
    elif len(found_views) > 0:
        cur_view = found_views[0]
        strs = cur_view.fetch_data()
        await message.answer('\n'.join(strs), parse_mode='HTML')
    else:
        await message.reply('???????????????? ??????????????')


for form in form_library:
    form.fill_states()
    dp.register_message_handler(mess_handler, state=form.state_group)
    dp.register_message_handler(command_handler, commands=form.command)

for view in view_library:
    dp.register_message_handler(command_handler, commands=view.command)


@dp.message_handler(state='*', commands=['start'])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    logging.info(f"{user_id}:{user_full_name} {time.asctime()}")
    await message.reply(
        "?????? ?????? ???????? ???????????? ?? ?????????????? ???????????????? ?????????????? ?????????????????????? ???????? ?????????????????? ?? ???????????????? ?? ???? ???? "
        "?????????????????? ??????????????. \n?????????? ??????????????! ")


async def setup_bot_commands(param):
    form_commands = [types.BotCommand(command="/"+frm.command, description=frm.title) for frm in form_library]
    view_commands = [types.BotCommand(command="/"+view.command, description=view.title) for view in view_library]
    bot_commands = form_commands + view_commands
    bot_commands.append(types.BotCommand(command="/start", description="?????????????????? ????????????????????"))
    await bot.set_my_commands(bot_commands)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=setup_bot_commands)
