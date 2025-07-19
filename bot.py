import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from telethon import TelegramClient
from telethon.errors import FloodWaitError
import time

# 🔐 Твои данные:
BOT_TOKEN = '7927213620:AAHJ68DsfyM8F3_k36HbIiJMMt1c88zQtXM'
OWNER_ID = 7620745738  # только ты можешь управлять
API_ID = 23283117
API_HASH = 'b25b0a34e0049f91795df9905c7a3a85'

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
tele_client = TelegramClient("session_rassylka", API_ID, API_HASH)

user_state = {}

@dp.message(Command("start"))
async def start(msg: Message):
    if msg.from_user.id != OWNER_ID:
        return await msg.answer("⛔ Ты не имеешь доступа.")
    await msg.answer("Привет! Введи список чатов (через запятую):")
    user_state[msg.from_user.id] = {"step": "chats"}

@dp.message(F.text)
async def handle_input(msg: Message):
    if msg.from_user.id != OWNER_ID:
        return

    state = user_state.get(msg.from_user.id, {})

    if state.get("step") == "chats":
        state["chats"] = [x.strip() for x in msg.text.split(",")]
        state["step"] = "message"
        await msg.answer("Теперь введи сообщение для рассылки:")

    elif state.get("step") == "message":
        state["message"] = msg.text
        state["step"] = "cooldown"
        await msg.answer("Теперь введи кулдаун между сообщениями (в секундах):")

    elif state.get("step") == "cooldown":
        try:
            state["cooldown"] = float(msg.text)
        except:
            return await msg.answer("⛔ Введи число, например 2.5")

        await msg.answer("✅ Начинаю рассылку...")
        await start_rassylka(msg, state)

async def start_rassylka(msg, state):
    try:
        await tele_client.start()
    except Exception as e:
        return await msg.answer(f"Ошибка авторизации Telethon: {e}")

    for chat in state["chats"]:
        try:
            await tele_client.send_message(chat, state["message"])
            await msg.answer(f"✅ Отправлено в {chat}")
        except FloodWaitError as e:
            await msg.answer(f"⏳ FloodWait: ждём {e.seconds} сек...")
            time.sleep(e.seconds)
        except Exception as e:
            await msg.answer(f"❌ Ошибка для {chat}: {e}")
        await asyncio.sleep(state["cooldown"])

    await msg.answer("🎉 Рассылка завершена!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
