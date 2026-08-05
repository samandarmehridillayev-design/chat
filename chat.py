import logging
import asyncio
import os
from collections import defaultdict
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import g4f
from g4f.client import Client

# ==========================================
# ⚙️ SOZLAMALAR
# ==========================================
# Tokenni xavfsizlik uchun Render Environment Variables'dan olish tavsiya etiladi
BOT_TOKEN = os.getenv("BOT_TOKEN", "8707856925:AAGJvwVNXc5a2eBhVM52vCsK9WQ9YQAXXsg")
REQUIRED_CHANNEL = "@samandarmehridillayev"
ADMIN_ID = 8004582786

USERS_DB = {}
CHAT_HISTORY = defaultdict(list)
MAX_HISTORY = 12                          # Suhbat xotirasi (so'nggi 12 ta xabar)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
scheduler = AsyncIOScheduler()
ai_client = Client()

logging.basicConfig(level=logging.INFO)


# ==========================================
# ✨ HASHAMATLI MATNLAR VA SHRIFTLAR
# ==========================================
class LuxuryText:
    @staticmethod
    def start(lang: str) -> str:
        if lang == "uz":
            return (
                "╔══════════════════════════╗\n"
                "║   ✨ 𝓢𝓪𝓶𝓪𝓷𝓭𝓪𝓻 𝓜𝓮𝓱𝓻𝓲𝓭𝓲𝓵𝓵𝓪𝔂𝓮𝝿  ║\n"
                "║      𝓟𝓻𝓮𝓶𝓲𝓾𝓶 𝓐𝓘 𝓑𝓸𝓽      ║\n"
                "╚══════════════════════════╝\n\n"
                "🪐  *Koinotning eng aqlli sun’iy intellektiga xush kelibsiz.*\n\n"
                "💎 Men oddiy bot emasman.\n"
                "   Men — sizning shaxsiy aqlli maslahatchingizman.\n\n"
                "🧠  Suhbatni eslab qolaman.\n"
                "🎯  Chuqur va aniq javob beraman.\n"
                "✨  Har bir so‘zingizni tushunaman.\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🗣  Savolingizni yozing..."
            )
        elif lang == "ru":
            return (
                "╔══════════════════════════╗\n"
                "║   ✨ 𝓢𝓪𝓶𝓪𝓷𝓭𝓪𝓻 𝓜𝓮𝓱𝓻𝓲𝓭𝓲𝓵𝓵𝓪𝔂𝓮𝝿  ║\n"
                "║      𝓟𝓻𝓮𝓶𝓲𝓾𝓶 𝓐𝓘 𝓑𝓸𝓽      ║\n"
                "╚══════════════════════════╝\n\n"
                "🪐  *Добро пожаловать в самый умный ИИ.*\n\n"
                "💎 Я не обычный бот.\n"
                "   Я — ваш персональный интеллектуальный помощник.\n\n"
                "🧠  Помню весь наш разговор.\n"
                "🎯  Даю глубокие и точные ответы.\n"
                "✨  Понимаю каждое ваше слово.\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🗣  Напишите ваш вопрос..."
            )
        else:
            return (
                "╔══════════════════════════╗\n"
                "║   ✨ 𝓢𝓪𝓶𝓪𝓷𝓭𝓪𝓻 𝓜𝓮𝓱𝓻𝓲𝓭𝓲𝓵𝓵𝓪𝔂𝓮𝝿  ║\n"
                "║      𝓟𝓻𝓮𝓶𝓲𝓾𝓶 𝓐𝓘 𝓑𝓸𝓽      ║\n"
                "╚══════════════════════════╝\n\n"
                "🪐  *Welcome to the most intelligent AI system.*\n\n"
                "💎 I am not an ordinary bot.\n"
                "   I am your personal intelligent advisor.\n\n"
                "🧠  I remember our entire conversation.\n"
                "🎯  I give deep and precise answers.\n"
                "✨  I understand every word you say.\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🗣  Write your question..."
            )

    @staticmethod
    def thinking(lang: str) -> str:
        texts = {
            "uz": "🔮  𝓣𝓱𝓲𝓷𝓴𝓲𝓷𝓰...  \n✨  Aqlim ishlayapti, biroz kuting...",
            "ru": "🔮  𝓣𝓱𝓲𝓷𝓴𝓲𝓷𝓰...  \n✨  Мой разум работает, подождите...",
            "en": "🔮  𝓣𝓱𝓲𝓷𝓴𝓲𝓷𝓰...  \n✨  My mind is processing, please wait..."
        }
        return texts.get(lang, texts["uz"])

    @staticmethod
    def daily() -> str:
        return (
            "╔══════════════════════════╗\n"
            "║   🚀  𝓝𝓮𝔀  𝓓𝓪𝔂 • 𝓝𝓮𝔀  𝓘𝓭𝓮𝓪𝓼  ║\n"
            "╚══════════════════════════╝\n\n"
            "🧠  Bugun miyangizda yangi savollar bormi?\n\n"
            "Men doim shu yerda —\n"
            "chuqur fikrlar, aniq javoblar va ilhom uchun.\n\n"
            "✨  Keling, bugun ham biror narsani kashf etamiz."
        )


class BotStates(StatesGroup):
    choosing_language = State()
    main_chat = State()


# ==========================================
# 🛑 OBUNA TEKSHIRUVI
# ==========================================
async def check_subscription(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False


def get_sub_keyboard(lang: str) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    texts = {
        "uz": ("📢  Kanalga obuna bo‘lish", "✅  Tekshirish"),
        "ru": ("📢  Подписаться на канал", "✅  Проверить"),
        "en": ("📢  Subscribe to Channel", "✅  Check")
    }
    btn, check = texts.get(lang, texts["uz"])

    builder.button(text=btn, url=f"https://t.me/{REQUIRED_CHANNEL.replace('@', '')}")
    builder.button(text=check, callback_data="check_sub")
    builder.adjust(1)
    return builder


# ==========================================
# 📥 START + TIL TANLASH
# ==========================================
@dp.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    USERS_DB[user_id] = {"name": message.from_user.full_name, "lang": "uz"}
    CHAT_HISTORY[user_id].clear()

    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇿  O‘zbekcha", callback_data="lang_uz")
    builder.button(text="🇷🇺  Русский", callback_data="lang_ru")
    builder.button(text="🇬🇧  English", callback_data="lang_en")
    builder.adjust(1)

    await message.answer(
        "╔══════════════════════════╗\n"
        "║     🌐  𝓛𝓪𝓷𝓰𝓾𝓪𝓰𝓮  𝓢𝓮𝓵𝓮𝓬𝓽  ║\n"
        "╚══════════════════════════╝\n\n"
        "Iltimos, tilni tanlang\n"
        "Пожалуйста, выберите язык\n"
        "Please choose your language",
        reply_markup=builder.as_markup()
    )
    await state.set_state(BotStates.choosing_language)


@dp.callback_query(F.data.startswith("lang_"))
async def set_language(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    user_id = callback.from_user.id
    USERS_DB[user_id] = {"name": callback.from_user.full_name, "lang": lang}

    if not await check_subscription(user_id):
        msg = {
            "uz": "❌  Botdan foydalanish uchun kanalimizga a’zo bo‘lishingiz shart.",
            "ru": "❌  Для использования бота необходимо подписаться на канал.",
            "en": "❌  You must subscribe to the channel to use the bot."
        }
        await callback.message.edit_text(msg[lang], reply_markup=get_sub_keyboard(lang).as_markup())
        return

    await callback.message.edit_text(LuxuryText.start(lang), parse_mode="Markdown")
    await state.set_state(BotStates.main_chat)


@dp.callback_query(F.data == "check_sub")
async def verify_sub(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = USERS_DB.get(user_id, {}).get("lang", "uz")

    if await check_subscription(user_id):
        await callback.message.edit_text(LuxuryText.start(lang), parse_mode="Markdown")
        await state.set_state(BotStates.main_chat)
    else:
        await callback.answer("❌  Hali obuna bo‘lmadingiz!", show_alert=True)


# ==========================================
# 🧠 MUKAMMAL KONTEKSTLI AI
# ==========================================
@dp.message(F.text)
async def ai_chat_handler(message: types.Message):
    user_id = message.from_user.id
    lang = USERS_DB.get(user_id, {}).get("lang", "uz")

    if not await check_subscription(user_id):
        msg = {
            "uz": "A’zolikni yangilang ❌",
            "ru": "Обновите подписку ❌",
            "en": "Please check subscription ❌"
        }
        await message.answer(msg[lang], reply_markup=get_sub_keyboard(lang).as_markup())
        return

    waiting = await message.answer(LuxuryText.thinking(lang))

    try:
        history = CHAT_HISTORY[user_id]
        history.append({"role": "user", "content": message.text})

        if len(history) > MAX_HISTORY:
            history = history[-MAX_HISTORY:]
            CHAT_HISTORY[user_id] = history

        system_prompt = (
            "Siz Samandar Mehridillayev tomonidan yaratilgan premium darajadagi sun’iy intellektsiz. "
            "Siz o‘ta aqlli, chuqur fikrlaydigan, elegant va do‘stona yordamchisiz. "
            "Javoblaringiz oddiy va quruq bo‘lmasin. Har doim chiroyli, motivatsion, biroz hashamatli uslubda yozing. "
            "Suhbat kontekstini mukammal eslab turing. Foydalanuvchi oldingi javobga qo‘shimcha savol bersa — "
            "to‘liq tushunib, davom ettiring. Emojilardan o‘rinli foydalaning. "
            "Faqat o‘zbek, rus yoki ingliz tilida javob bering."
        )

        messages = [{"role": "system", "content": system_prompt}] + history

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: ai_client.chat.completions.create(
                model=g4f.models.default,
                messages=messages
            )
        )

        ai_reply = response.choices[0].message.content.strip()

        # Tarixga AI javobini ham qo‘shamiz
        history.append({"role": "assistant", "content": ai_reply})
        CHAT_HISTORY[user_id] = history

        final_text = (
            "╔══════════════════════════╗\n"
            "║      🤖  𝓐𝓘  𝓡𝓮𝓼𝓹𝓸𝓷𝓼𝓮      ║\n"
            "╚══════════════════════════╝\n\n"
            f"{ai_reply}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "✨  Samandar Mehridillayev • Premium AI"
        )

        await waiting.edit_text(final_text, parse_mode=None)

    except Exception as e:
        logging.error(f"AI Error: {e}")
        error_msg = {
            "uz": "🪐  Sun’iy intellekt hozir band. Birozdan so‘ng qayta urinib ko‘ring.",
            "ru": "🪐  Сеть ИИ сейчас перегружена. Попробуйте позже.",
            "en": "🪐  AI network is currently busy. Please try again later."
        }
        await waiting.edit_text(error_msg[lang])


# ==========================================
# 📅 KUNLIK XABAR
# ==========================================
async def send_daily_reminder():
    text = LuxuryText.daily()
    for user_id in list(USERS_DB.keys()):
        try:
            await bot.send_message(chat_id=user_id, text=text)
            await asyncio.sleep(0.07)
        except Exception:
            pass


# ==========================================
# 🌐 RENDER UCHUN DUMMY WEB SERVER
# ==========================================
async def handle(request):
    return web.Response(text="Bot is running smoothly on Render Free Tier!")


# ==========================================
# 🚀 ISHGA TUSHIRISH
# ==========================================
async def main():
    # Render uchun HTTP portni ochish
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    # Rejalashtirgichni ishga tushirish
    scheduler.add_job(send_daily_reminder, "cron", hour=9, minute=0)
    scheduler.start()

    print("✨ Premium AI Bot Render Bepul servisida ishga tushdi!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
