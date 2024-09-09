import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
import handlers
import config
import subprocess
bot_properties = DefaultBotProperties(parse_mode=ParseMode.HTML)
bot = Bot(token=config.BOT_TOKEN, default=bot_properties)


async def main():
    bot = Bot(token=config.BOT_TOKEN, default=bot_properties)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(handlers.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="a", format="%(asctime)s %(levelname)s %(message)s")
    current_env = os.environ.copy()
    python_exec = os.path.join(sys.prefix, 'bin', 'python')
    # subprocess.call('Notifications.py', env=current_env)
    # subprocess.Popen([python_exec, 'Notifications.py'])
    asyncio.run(main())

    # exec(open('Notifications.py').read())