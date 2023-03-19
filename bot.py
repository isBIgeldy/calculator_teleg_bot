import logging
import config
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

AVAILABLE_OPERATIONS = ['+', '-', '*', '/']

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class CalcStates(StatesGroup):
    waiting_for_first_number = State()
    waiting_for_operation = State()
    waiting_for_second_number = State()


async def start_calculation(message: types.Message):
    await message.answer('Напишите первое число: ')
    await CalcStates.waiting_for_first_number.set()


async def choosing_first_number(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Некоректный ввод. Попробуйте снова.')
        return
    await state.update_data(first_number=int(message.text))
    await CalcStates.next()
    await message.answer('Теперь введите операцию: ')


async def choosing_operation(message: types.Message, state: FSMContext):
    if message.text not in AVAILABLE_OPERATIONS:
        await message.answer('Недопустимая операция.Попробуйте снова.')
        return
    await state.update_data(operation=message.text)
    await CalcStates.next()
    await message.answer('Введите второе число: ')


async def choosing_second_number(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Некоректный ввод. Попробуйте снова.')
        return
    user_data = await state.get_data()
    oper = user_data['operation']
    first_number = user_data['first_number']
    second_number = int(message.text)
    result = 0
    if oper == '+':
        result = first_number+second_number
    elif oper == '-':
        result = first_number-second_number
    elif oper == '*':
        result = first_number*second_number
    elif oper == '/':
        result = first_number/second_number
    await message.answer(f'Результат {result}')
    await state.finish()


def register_handlers():
    dp.register_message_handler(
        start_calculation, commands='calc', state='*'
    )
    dp.register_message_handler(
        choosing_first_number, state=CalcStates.waiting_for_first_number
    )
    dp.register_message_handler(
        choosing_operation, state=CalcStates.waiting_for_operation
    )
    dp.register_message_handler(
        choosing_second_number, state=CalcStates.waiting_for_second_number
    )


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply("Hi!\nI'm calculator bot")


@dp.message_handler(commands=['cancel'])
async def cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply("Отмена.")

if __name__ == '__main__':
    register_handlers()
    executor.start_polling(dp, skip_updates=True)
