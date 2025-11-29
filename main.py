import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

# =====================================================
# 🔧 CONFIG
# =====================================================

TOKEN = "8466481934:AAHF7CmFwG4Sir5Jnn9VTAVqXVdLiMwpHQw"

ORDERS_CHAT_ID = -1003386429666
ORDERS_THREAD_ID = 4

SUPPORT_CHAT_ID = -1003386429666
SUPPORT_THREAD_ID = 2

bot = Bot(token=TOKEN)
dp = Dispatcher()

# =====================================================
# 🌍 ТЕКСТЫ ДЛЯ ВСЕХ ЯЗЫКОВ (ПОЛНЫЕ!)
# =====================================================

LANGUAGES = {
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
    "ua": "🇺🇦 Українська"
}

TEXTS = {
    "ru": {
        "start": "Выберите язык:",
        "menu": "Главное меню:",
        "settings": "⚙ Настройки",
        "order": "🛒 Заказать бота",
        "support": "🛠 Техническая поддержка",
        "process": "📦 Как будет проходить продажа",
        "info": "ℹ Информация",
        "my_orders": "📁 Мои заказы",
        "coop": "🤝 Сотрудничество",
        "ask_order": "Опишите какого бота вы хотите:",
        "ask_support": "Опишите вашу проблему:",
        "process_text": (
            "📦 *Как проходит продажа бота:*\n\n"
            "1️⃣ Вы оставляете заявку\n"
            "2️⃣ Мы уточняем детали\n"
            "3️⃣ Озвучиваем цену\n"
            "4️⃣ Создаём бота\n"
            "5️⃣ Отправляем вам бота\n"
            "6️⃣ Вы получаете поддержку 🛠"
        ),
        "info_text": (
            "ℹ *Информация*\n\n"
            "Мы создаём Telegram-ботов любой сложности.\n"
            "Работаем быстро, качественно и с поддержкой 24/7."
        ),
        "coop_text": (
            "🤝 *Сотрудничество*\n\n"
            "Мы всегда открыты партнёрству.\n"
            "Пишите ваши предложения — обсудим!"
        ),
        "no_orders": "📁 У вас пока нет заказов."
    },

    "en": {
        "start": "Choose your language:",
        "menu": "Main menu:",
        "settings": "⚙ Settings",
        "order": "🛒 Order a bot",
        "support": "🛠 Technical support",
        "process": "📦 How the sale works",
        "info": "ℹ Information",
        "my_orders": "📁 My orders",
        "coop": "🤝 Cooperation",
        "ask_order": "Describe the bot you want:",
        "ask_support": "Describe your issue:",
        "process_text": (
            "📦 *How the bot purchase works:*\n\n"
            "1️⃣ You submit a request\n"
            "2️⃣ We clarify the details\n"
            "3️⃣ You receive a price quote\n"
            "4️⃣ We develop your bot\n"
            "5️⃣ You receive the final product\n"
            "6️⃣ You get full support 🛠"
        ),
        "info_text": (
            "ℹ *Information*\n\n"
            "We create Telegram bots of any complexity.\n"
            "Fast delivery, high quality, 24/7 support."
        ),
        "coop_text": (
            "🤝 *Cooperation*\n\n"
            "We are open to partnership.\n"
            "Feel free to send your ideas!"
        ),
        "no_orders": "📁 You have no orders yet."
    },

    "ua": {
        "start": "Оберіть мову:",
        "menu": "Головне меню:",
        "settings": "⚙ Налаштування",
        "order": "🛒 Замовити бота",
        "support": "🛠 Підтримка",
        "process": "📦 Як проходить продаж",
        "info": "ℹ Інформація",
        "my_orders": "📁 Мої замовлення",
        "coop": "🤝 Співпраця",
        "ask_order": "Опишіть, якого бота ви хочете:",
        "ask_support": "Опишіть вашу проблему:",
        "process_text": (
            "📦 *Як проходить продаж бота:*\n\n"
            "1️⃣ Ви залишаєте заявку\n"
            "2️⃣ Ми уточнюємо деталі\n"
            "3️⃣ Ви отримуєте ціну\n"
            "4️⃣ Ми створюємо бота\n"
            "5️⃣ Ви отримуєте готовий продукт\n"
            "6️⃣ Ви отримуєте підтримку 🛠"
        ),
        "info_text": (
            "ℹ *Інформація*\n\n"
            "Ми створюємо Telegram-ботів будь-якої складності.\n"
            "Швидко, якісно та з підтримкою 24/7."
        ),
        "coop_text": (
            "🤝 *Співпраця*\n\n"
            "Ми відкриті до партнерства.\n"
            "Пишіть свої пропозиції!"
        ),
        "no_orders": "📁 У вас ще немає замовлень."
    }
}

user_lang = {}

# =====================================================
# START
# =====================================================

@dp.message(F.text == "/start")
async def start_cmd(msg: Message):
    kb = InlineKeyboardBuilder()
    for code, label in LANGUAGES.items():
        kb.button(text=label, callback_data=f"lang_{code}")
    kb.adjust(1)
    await msg.answer("🌐 Выберите язык / Choose language / Оберіть мову:", reply_markup=kb.as_markup())

# =====================================================
# ВЫБОР ЯЗЫКА
# =====================================================

@dp.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    user_lang[callback.from_user.id] = lang
    await callback.message.edit_text(TEXTS[lang]["menu"], reply_markup=main_menu(lang))

# =====================================================
# МЕНЮ
# =====================================================

def main_menu(lang):
    t = TEXTS[lang]
    kb = InlineKeyboardBuilder()
    kb.button(text=t["settings"], callback_data="menu_settings")
    kb.button(text=t["order"], callback_data="menu_order")
    kb.button(text=t["support"], callback_data="menu_support")
    kb.button(text=t["process"], callback_data="menu_process")
    kb.button(text=t["info"], callback_data="menu_info")
    kb.button(text=t["my_orders"], callback_data="menu_my_orders")
    kb.button(text=t["coop"], callback_data="menu_coop")
    kb.adjust(1)
    return kb.as_markup()

# =====================================================
# ЗАКАЗ БОТА
# =====================================================

@dp.callback_query(F.data == "menu_order")
async def order_btn(callback: CallbackQuery):
    lang = user_lang.get(callback.from_user.id, "ru")
    await callback.message.answer(TEXTS[lang]["ask_order"])
    dp.message.register(order_received, F.chat.id == callback.message.chat.id)

async def order_received(msg: Message):
    await bot.send_message(
        chat_id=ORDERS_CHAT_ID,
        message_thread_id=ORDERS_THREAD_ID,
        text=f"🛒 НОВЫЙ ЗАКАЗ\n\n"
             f"От: @{msg.from_user.username}\n"
             f"ID: {msg.from_user.id}\n\n"
             f"Заявка:\n{msg.text}"
    )
    await msg.answer("Ваш заказ отправлен! 🎉")

# =====================================================
# ТЕХПОДДЕРЖКА
# =====================================================

@dp.callback_query(F.data == "menu_support")
async def support_btn(callback: CallbackQuery):
    lang = user_lang.get(callback.from_user.id, "ru")
    await callback.message.answer(TEXTS[lang]["ask_support"])
    dp.message.register(support_received, F.chat.id == callback.message.chat.id)

async def support_received(msg: Message):
    await bot.send_message(
        chat_id=SUPPORT_CHAT_ID,
        message_thread_id=SUPPORT_THREAD_ID,
        text=f"🛠 НОВОЕ ОБРАЩЕНИЕ В ПОДДЕРЖКУ\n\n"
             f"От: @{msg.from_user.username}\n"
             f"ID: {msg.from_user.id}\n\n"
             f"Сообщение:\n{msg.text}"
    )
    await msg.answer("Ваше сообщение отправлено! 🙌")

# =====================================================
# ПРОЧИЕ КНОПКИ
# =====================================================

@dp.callback_query(F.data.startswith("menu_"))
async def other_buttons(callback: CallbackQuery):
    lang = user_lang.get(callback.from_user.id, "ru")
    t = TEXTS[lang]

    mapping = {
        "menu_process": t["process_text"],
        "menu_info": t["info_text"],
        "menu_my_orders": t["no_orders"],
        "menu_coop": t["coop_text"],
        "menu_settings": t["settings"]
    }

    if callback.data in mapping:
        await callback.message.answer(mapping[callback.data], parse_mode="Markdown")


# =====================================================
# START BOT
# =====================================================

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
