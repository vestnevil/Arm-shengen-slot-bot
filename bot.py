import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

API_TOKEN = '7986416500:AAF1TASC9S_2Lkth0dLKpj7wxV4vpGG2Fb4'
MY_USER_ID = 414938139
TARGET_CHAT_ID = -1002194273388

KEYWORDS = ["слот", "слоты", "появились", "выложил", "запись"]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# —— Алерт при ключе в канале
@dp.message(F.chat.id == TARGET_CHAT_ID)
async def channel_handler(message: types.Message):
    text = (message.text or message.caption or "").lower()
    if any(kw in text for kw in KEYWORDS):
        alert = (
            f"СРОЧНО! Слот или запись в @shengen_am\n\n"
            f"Текст: {message.text or message.caption or '[фото/документ]'}\n"
            f"<a href='{message.link}'>ПЕРЕЙТИ К СООБЩЕНИЮ</a>"
        )
        await bot.send_message(MY_USER_ID, alert, disable_web_page_preview=True)

# —— Команды в личке (сразу отвечаем всем, потом можно будет ограничить)
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Бот запущен и следит за слотами в @shengen_am\nПроверь: /ping")

@dp.message(Command("ping"))
async def ping(message: types.Message):
    await message.answer("Живой! Следит за слотами 24/7 ✅\nЕсли видишь это сообщение — всё работает идеально")

async def main():
    print("Бот запущен на Railway — следит за @shengen_am")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
