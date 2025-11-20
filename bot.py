import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# --- Configuration (Read from Environment Variables) ---
# IMPORTANT: You must set these variables in your Railway project dashboard.
# DO NOT hardcode your token and IDs here in a production environment.
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not API_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set.")

try:
    MY_USER_ID = int(os.getenv('MY_USER_ID'))
    TARGET_CHAT_ID = int(os.getenv('TARGET_CHAT_ID'))
except (TypeError, ValueError) as e:
    raise ValueError(f"MY_USER_ID or TARGET_CHAT_ID environment variable is missing or invalid: {e}")

KEYWORDS = ["слот", "слоты", "появились", "выложил", "запись"]

# --- Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# --- Utility to Safely Get Channel Link ---
def get_channel_message_link(chat_id: int, message_id: int) -> str:
    """Constructs a t.me link for a message in a channel."""
    # Private channel IDs start with -100. We need to remove the -100 prefix.
    # The format is t.me/c/ChannelID_without_-100/MessageID
    
    # We use a safe default construction for private channels.
    # Note: Accessing this link requires the user to be a member of the channel.
    channel_path = str(chat_id).replace('-100', '')
    return f"https://t.me/c/{channel_path}/{message_id}"


# —— Алерт при ключе в канале
@dp.message(F.chat.id == TARGET_CHAT_ID)
async def channel_handler(message: types.Message):
    try:
        # Get text, prioritizing text, then caption, defaulting to empty string
        text = (message.text or message.caption or "").lower()
        
        # Check for keywords
        if any(kw in text for kw in KEYWORDS):
            
            # Construct a safe link to the original message
            message_link = get_channel_message_link(message.chat.id, message.message_id)
            
            # Prepare the alert text
            alert = (
                f"🚨 **СРОЧНО! Слот или запись** в @shengen_am\n\n"
                f"**Текст:** {message.text or message.caption or '[фото/документ]'}\n"
                f"<a href='{message_link}'>🚀 ПЕРЕЙТИ К СООБЩЕНИЮ</a>"
            )
            
            # Send alert to MY_USER_ID
            await bot.send_message(
                MY_USER_ID, 
                alert, 
                disable_web_page_preview=True,
                parse_mode=ParseMode.MARKDOWN
            )

    except Exception as e:
        # Log the detailed error to the console/Railway logs
        logging.error(f"Error processing channel message (ID {message.message_id}) in chat {message.chat.id}: {e}", exc_info=True)
        
        # Optionally, send an error notification to yourself
        await bot.send_message(MY_USER_ID, f"Bot encountered an error in channel handler:\n`{type(e).__name__}: {str(e)}`", parse_mode=ParseMode.MARKDOWN)


# —— Команды в личке
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Бот запущен и следит за слотами в @shengen_am\nПроверь: /ping")

@dp.message(Command("ping"))
async def ping(message: types.Message):
    await message.answer("Живой! Следит за слотами 24/7 ✅\nЕсли видишь это сообщение — всё работает идеально")

# --- Main Runner ---
async def main():
    logging.info("Starting bot on Railway...")
    # This will run the bot, using long polling to receive updates
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped manually.")
    except Exception as e:
        logging.critical(f"Fatal error during bot startup: {e}", exc_info=True)
