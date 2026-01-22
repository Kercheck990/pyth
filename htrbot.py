import asyncio
import logging
import os
import aiosqlite
from datetime import datetime
from typing import Union

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(i.strip()) for i in os.getenv("ADMIN_IDS", "").split(",") if i.strip()]
CHANNEL_1 = "@Hunter_nftbattle"
CHANNEL_2 = "@hntrnft"
OWNER = "@scive"

if not TOKEN:
    exit("Error: BOT_TOKEN not found in .env file")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
bot = Bot(token=TOKEN)
dp = Dispatcher()

DB_PATH = "database.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                ref_count INTEGER DEFAULT 0,
                created_at TEXT,
                referrer TEXT,
                is_verified INTEGER DEFAULT 0
            )
        """)
        await db.commit()

async def check_subscription(user_id: int) -> bool:
    for channel in [CHANNEL_1, CHANNEL_2]:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ["member", "administrator", "creator", "restricted"]:
                continue
            return False
        except Exception as e:
            logger.error(f"Check error {channel}: {e}")
            return False
    return True

def get_main_kb():
    kb = [
        [KeyboardButton(text="👤 Профиль")],
        [KeyboardButton(text="🎁 Призы за рефералов")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = str(message.from_user.id)
    args = message.text.split()
    referrer_id = args[1] if len(args) > 1 else None

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT is_verified FROM users WHERE user_id = ?", (user_id,)) as cursor:
            user_row = await cursor.fetchone()

        is_new_user = False
        if user_row is None:
            is_new_user = True
            created_at = datetime.now().strftime("%d.%m.%Y")
            ref_to_save = referrer_id if referrer_id != user_id else None
            await db.execute(
                "INSERT INTO users (user_id, ref_count, created_at, referrer, is_verified) VALUES (?, ?, ?, ?, ?)",
                (user_id, 0, created_at, ref_to_save, 0)
            )
            await db.commit()
            is_verified = 0
        else:
            is_verified = user_row[0]

    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\nДобро пожаловать в Hunter Referrals Bot.",
        reply_markup=get_main_kb()
    )

    if is_new_user or not is_verified:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Подписаться на Hunter NFT", url=f"https://t.me/{CHANNEL_1[1:]}"))
        builder.row(InlineKeyboardButton(text="Подписаться на HNTR", url=f"https://t.me/{CHANNEL_2[1:]}"))
        builder.row(InlineKeyboardButton(text="✅ Проверить подписки", callback_data="check_subs"))
        await message.answer("Для активации профиля подпишись на каналы:", reply_markup=builder.as_markup())
    else:
        await show_profile(message)

@dp.callback_query(F.data == "check_subs")
async def process_check_subs(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    if await check_subscription(callback.from_user.id):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT is_verified, referrer FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
            if row and not row[0]:
                await db.execute("UPDATE users SET is_verified = 1 WHERE user_id = ?", (user_id,))
                if row[1]:
                    await db.execute("UPDATE users SET ref_count = ref_count + 1 WHERE user_id = ?", (row[1],))
                    try: await bot.send_message(int(row[1]), "🎉 У вас новый активный реферал! (+1)")
                    except: pass
                await db.commit()
                await callback.message.edit_text("✅ Подписки подтверждены!")
                await show_profile(callback.message, callback.from_user.id)
            else:
                await callback.answer("Уже подтверждено!", show_alert=True)
    else:
        await callback.answer("❌ Подпишитесь на оба канала!", show_alert=True)

async def show_profile(message: Union[types.Message, types.CallbackQuery], manual_id: int = None):
    uid = str(manual_id or message.from_user.id)
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT ref_count, created_at, is_verified FROM users WHERE user_id = ?", (uid,)) as cursor:
            user_data = await cursor.fetchone()
    
    if not user_data:
        if manual_id: await message.answer("ID не найден.")
        return
    
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={uid}"
    
    text = (
        f"👤 Профиль {uid}\n\n"
        f"📊 Рефералов: {user_data[0]}\n"
        f"📅 Регистрация: {user_data[1]}\n"
        f"👑 Владелец: {OWNER}\n\n"
        f"🔗 Реф. ссылка:\n`{ref_link}`"
    )
    if isinstance(message, types.Message): await message.answer(text, parse_mode="Markdown")
    else: await message.message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "👤 Профиль")
async def menu_profile(message: types.Message): await show_profile(message)

@dp.message(Command("profile"))
async def cmd_profile(message: types.Message): await show_profile(message)

@dp.message(F.text == "🎁 Призы за рефералов")
async def menu_prizes(message: types.Message):
    text = (
        "🎁 Призы за рефералов:\n\n"
        "10 рефералов — 100кк (100.000.000 звёзд)\n"
        "50 рефералов — 500кк (500.000.000звёзд)\n"
        "100 рефералов — 1ккк (1.000.000.000 звёзд)\n\n"
        "👤 Выдача: " + OWNER
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("user"))
async def admin_user(message: types.Message):
    if message.from_user.id not in ADMIN_IDS: return
    args = message.text.split()
    if len(args) < 2: return await message.answer("Пример: /user ID")
    await show_profile(message, manual_id=int(args[1]))

@dp.message(Command("checkstats"))
async def admin_stats(message: types.Message):
    if message.from_user.id not in ADMIN_IDS: return
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*), SUM(is_verified), SUM(ref_count) FROM users") as c:
            data = await c.fetchone()
    text = (
        "📊 Статистика:\n\n"
        f"Всего в боте: {data[0]}\n"
        f"Подписаны на канал: {data[1] or 0}\n"
        f"Всего реф-к: {data[2] or 0}"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("rf"))
async def admin_rf(message: types.Message):
    if message.from_user.id not in ADMIN_IDS: return
    text = message.text.replace("/rf", "").strip()
    if not text: return await message.answer("Пиши текст после /rf")
    
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            users = await cursor.fetchall()
    
    ok = 0
    await message.answer(f"Запуск на {len(users)} чел.")
    for u in users:
        try:
            await bot.send_message(u[0], text)
            ok += 1
            await asyncio.sleep(0.05)
        except (TelegramForbiddenError, Exception): continue
    await message.answer(f"Готово! Получили: {ok}")

async def main():
    await init_db() 
    await dp.start_polling(bot)

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: pass