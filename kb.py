from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


exit_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="◀️ Выйти в меню")]], resize_keyboard=True)

menu = [
    [InlineKeyboardButton(text="Просмотреть мои финансы", callback_data="/my_deposits")],
    [InlineKeyboardButton(text="Добавить вклад или счет", callback_data="/add_deposit")],
    [InlineKeyboardButton(text="Посчитать доход за период", callback_data="/calculate_income")]
]

my_deposits = [
    [InlineKeyboardButton(text="Подробнее", callback_data="/my_deposits_more")],
    [InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="/menu")]
]

inline_menu_1btn = [
    [InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="/menu")]
]

yes_no = [
    [InlineKeyboardButton(text="ДА", callback_data="/YES")],
    [InlineKeyboardButton(text="НЕТ", callback_data="/NO")]
]

add_depo_type = [
    [InlineKeyboardButton(text="Вклад", callback_data="/d_type_deposit")],
    [InlineKeyboardButton(text="Накопительный счет", callback_data="/d_type_other")]
]
add_depo_type = InlineKeyboardMarkup(inline_keyboard=add_depo_type)
yes_no = InlineKeyboardMarkup(inline_keyboard=yes_no)
inline_menu_1btn = InlineKeyboardMarkup(inline_keyboard=inline_menu_1btn)
my_deposits = InlineKeyboardMarkup(inline_keyboard=my_deposits)
menu = InlineKeyboardMarkup(inline_keyboard=menu)
# settings = InlineKeyboardMarkup(inline_keyboard=settings)
