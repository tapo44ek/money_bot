import backend as data_module
import re
import os
import sys
from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from main import bot
import kb
import text
import subprocess
import multiprocessing as mp

router = Router()


class UserData(StatesGroup):
    lastmsg = State()
    start_period = State()
    end_period = State()
    bank = State()
    amount = State()
    start_date = State()
    end_date = State()
    rate = State()
    com_int = State()
    type = State()


@router.callback_query(F.data == "/add_deposit")
async def add_deposit(callback: types.CallbackQuery, state: FSMContext):
    # print(msg.text)
    # result = data_module.search(msg.text, msg.from_user.id)
    # data_module.chat_checker(msg.from_user.id, msg.chat.id)
    await callback.answer(
        text="Успешно",
        show_alert=False
    )
    await state.set_state(UserData.type)
    await callback.message.answer('Добавить Вклад или Накопительный счет?', reply_markup=kb.add_depo_type)
    # await state.set_state(UserActions.phone_helper)


@router.callback_query(UserData.type)
async def add_deposit(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == '/d_type_deposit':
        await state.update_data(type='Вклад')
        await callback.answer(
            text="Успешно",
            show_alert=False
        )
        await callback.message.answer(
            text="В каком банке?"
        )
        await state.set_state(UserData.bank)
    elif callback.data == '/d_type_other':
        await state.update_data(type='Накопительный счет')
        await callback.answer(
            text="Успешно",
            show_alert=False
        )
        await callback.message.answer(
            text="В каком банке?"
        )
        await state.set_state(UserData.bank)


@router.message(UserData.bank)
async def add_deposit(msg: Message, state: FSMContext):
    await state.update_data(bank=msg.text)
    await msg.answer(
        text="Теперь введи дату начала вклада в формате ДД.ММ.ГГГ"
    )
    await state.set_state(UserData.start_date)


@router.message(UserData.start_date)
async def add_deposit(msg: Message, state: FSMContext):
    date_pattern = r'^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.([0-9]{4})$'
    if re.match(date_pattern, msg.text):
        await state.update_data(start_date=msg.text)
        await msg.answer(
            text="Теперь введи дату окончания вкладаа в формате ДД.ММ.ГГГ"
        )
        await state.set_state(UserData.end_date)
    else:
        await msg.answer('Неверный формат!\nВведи дату начала вклада в формате ДД.ММ.ГГГ')


@router.message(UserData.end_date)
async def add_deposit(msg: Message, state: FSMContext):
    date_pattern = r'^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.([0-9]{4})$'
    if re.match(date_pattern, msg.text):
        await state.update_data(end_date=msg.text)
        await msg.answer(
            text="Теперь введи сумму вклада в рублях (целое число)"
        )
        await state.set_state(UserData.amount)
    else:
        await msg.answer('Неверный формат!\nВведи дату начала вклада в формате ДД.ММ.ГГГ')


@router.message(UserData.amount)
async def add_deposit(msg: Message, state: FSMContext):
    pattern = r'^-?[0-9]+$'
    if re.match(pattern, msg.text):
        await state.update_data(amount=msg.text)
        await msg.answer(
            text="Теперь введи годовую ставку в процентах"
        )
        await state.set_state(UserData.rate)
    else:
        await msg.answer('Неверный формат!\nВведено не целое число')


@router.message(UserData.rate)
async def add_deposit(msg: Message, state: FSMContext):

    pattern = r'''^[0-9.,;:!?"'%()-]+$'''
    if re.match(pattern, msg.text):
        rate_ = msg.text

        try:
            rate_ = rate_.split('%')[0]
        except:
            pass

        try:
            rate_ = rate_.replace(',', '.')
        except:
            pass

        if not '0.' in rate_:
            rate_ = float(rate_)

        if rate_ > 0.9:
            rate_ = rate_ / 100
            rate_ = str(rate_)

        await state.update_data(rate=rate_)
        await msg.answer(
            text="Вклад/счет с капитализацией?",
            reply_markup=kb.yes_no
        )
        await state.set_state(UserData.com_int)
    else:
        await msg.answer('Неверный формат!\nПовторите ввод')


@router.callback_query(UserData.com_int)
async def add_deposit(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    if callback.data == '/YES':
        await callback.answer(
            text="Успешно",
            show_alert=False
        )
        await callback.message.answer(
            text=data_module.add_deposit(user_data['bank'],
                                         user_data['amount'],
                                         user_data['start_date'],
                                         user_data['end_date'],
                                         user_data['rate'],
                                         True,
                                         callback.from_user.id,
                                         user_data['type']),
            reply_markup=kb.inline_menu_1btn
        )
        await state.clear()
    elif callback.data == '/NO':
        await callback.answer(
            text="Успешно",
            show_alert=False
        )
        await callback.message.answer(
            text=data_module.add_deposit(user_data['bank'],
                                         user_data['amount'],
                                         user_data['start_date'],
                                         user_data['end_date'],
                                         user_data['rate'],
                                         False,
                                         callback.from_user.id,
                                         user_data['type']),
            reply_markup=kb.inline_menu_1btn
        )
        await state.clear()


#####################
@router.callback_query(F.data == "/calculate_income")
async def calc_details(callback: types.CallbackQuery, state: FSMContext):
    # print(msg.text)
    # result = data_module.search(msg.text, msg.from_user.id)
    # data_module.chat_checker(msg.from_user.id, msg.chat.id)
    await state.set_state(UserData.start_period)
    await callback.message.answer('Введи дату начала периода в формате ДД.ММ.ГГГ')
    # await state.set_state(UserActions.phone_helper)
    await callback.answer(
        text="Успешно",
        show_alert=False
    )


@router.message(UserData.start_period)
async def set_start(msg: Message, state: FSMContext):
    date_pattern = r'^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.([0-9]{4})$'
    if re.match(date_pattern, msg.text):
        await state.update_data(start_period=msg.text)
        await msg.answer(
            text="Теперь введи дату окончания периода в формате ДД.ММ.ГГГ"
        )
        await state.set_state(UserData.end_period)
    else:
        await msg.answer('Неверный формат!\nВведи дату старта в формате ДД.ММ.ГГГ')


@router.callback_query(F.data == "/YES", UserData.end_period)
async def calc_details(callback: types.CallbackQuery, state: FSMContext):
    # print(msg.text)
    # result = data_module.search(msg.text, msg.from_user.id)
    # data_module.chat_checker(msg.from_user.id, msg.chat.id)
    user_data = await state.get_data()
    await callback.message.answer(data_module.get_profit(callback.from_user.id,
                                                         user_data['start_period'],
                                                         user_data['end_period'],
                                                         True), reply_markup=kb.inline_menu_1btn)
    # await state.set_state(UserActions.phone_helper)
    await callback.answer(
        text="Успешно",
        show_alert=False
    )


@router.callback_query(F.data == "/NO", UserData.end_period)
async def calc_details(callback: types.CallbackQuery, state: FSMContext):
    # print(msg.text)
    # result = data_module.search(msg.text, msg.from_user.id)
    # data_module.chat_checker(msg.from_user.id, msg.chat.id)
    user_data = await state.get_data()
    await callback.message.answer(data_module.get_profit(callback.from_user.id,
                                                         user_data['start_period'],
                                                         user_data['end_period'],
                                                         False), reply_markup=kb.inline_menu_1btn)
    # await state.set_state(UserActions.phone_helper)
    await callback.answer(
        text="Успешно",
        show_alert=False
    )


@router.message(UserData.end_period)
async def set_end(msg: Message, state: FSMContext):
    date_pattern = r'^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.([0-9]{4})$'
    if re.match(date_pattern, msg.text):
        await state.update_data(end_period=msg.text)
        await msg.answer(
            text="Нужна ли детализация по счетам и вкладам?",
            reply_markup=kb.yes_no
        )
    else:
        await msg.answer('Неверный формат!\nВведи дату окончания в формате ДД.ММ.ГГГ')


@router.message(Command("start"))
async def start_handler(msg: Message, state: FSMContext):
    await msg.answer('Привет, я бот - помощник по финансам', reply_markup=kb.exit_kb)


@router.message(F.text == '◀️ Выйти в меню')
async def menu(msg: Message, state: FSMContext):
    # print(msg.text)
    # result = data_module.search(msg.text, msg.from_user.id)
    # data_module.chat_checker(msg.from_user.id, msg.chat.id)
    await msg.answer('Вот, что ты можешь сделать:', reply_markup=kb.menu)
    # await state.set_state(UserActions.phone_helper)


@router.callback_query(F.data == "/menu")
async def menu_inline(callback: types.CallbackQuery):
    # print(msg.text)
    # result = data_module.search(msg.text, msg.from_user.id)
    # data_module.chat_checker(msg.from_user.id, msg.chat.id)
    await callback.message.answer('Вот, что ты можешь сделать:', reply_markup=kb.menu)
    # await state.set_state(UserActions.phone_helper)
    await callback.answer(
        text="Успешно",
        show_alert=False
    )


@router.callback_query(F.data == "/my_deposits_more")
async def deposits_info(callback: types.CallbackQuery):
    # print(msg.text)
    # result = data_module.search(msg.text, msg.from_user.id)
    # data_module.chat_checker(msg.from_user.id, msg.chat.id)
    await callback.message.answer(data_module.get_deposits(callback.from_user.id), reply_markup=kb.inline_menu_1btn)
    # await state.set_state(UserActions.phone_helper)
    await callback.answer(
        text="Успешно",
        show_alert=False
    )


# @router.message(F.text == "отправь сообщение")
# async def menu(bot: bot):
#     await bot.send_message(chat_id=309025156, text='<b>напиши мне что-нибудь</b>')


@router.callback_query(F.data == "/my_deposits")
async def helper_status(callback: types.CallbackQuery, state: FSMContext):
    count_, sum_ = data_module.get_amount(callback.from_user.id)
    await callback.message.answer(text.count_n_sum.format(count=count_, sum=sum_), reply_markup=kb.my_deposits)
    await callback.answer(
        text="Успешно",
        show_alert=False
    )