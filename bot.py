import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# ========================= CONFIG =========================
API_TOKEN = '7986416500:AAF1TASC9S_2Lkth0dLKpj7wxV4vpGG2Fb4'
MY_USER_ID = 414938139
TARGET_CHAT_ID = -1002194273388

KEYWORDS = ["слот", "слоты", "появились", "выложила", "запись"]
# ==========================================================

logging.basicConfig(level=logging.INFO)

# ←←← ВОТ ЭТА СТРОКА ИСПРАВЛЕНА ДЛЯ НОВОЙ ВЕРСИИ aiogram
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

async def send_alert(message: types.Message):
    alert_text = (
        f"СРОЧНО! Слот или запись в @shengen_am\n\n"
        f"Текст: {message.text or message.caption or '[фото/документ]'}\n"
        f"<a href='{message.link}'>ПЕРЕЙТИ К СООБЩЕНИЮ</a>"
    )
    await bot.send_message(MY_USER_ID, alert_text, disable_web_page_preview=True)

@dp.message()
async def check_message(message: types.Message):
    if message.chat.id != TARGET_CHAT_ID:
        return
    text = (message.text or message.caption or "").lower()
    if any(kw in text for kw in KEYWORDS):
        await send_alert(message)

@dp.message(Command("ping"))
async def ping(m: types.Message):
    if m.from_user.id == MY_USER_ID:
        await m.answer("Живой! Следит за слотами 24/7 ✅")

async def main():
    print("Бот запущен на Railway — следит за @shengen_am")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
