import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.filters import Command
from game_logic import *
from database import *
from admin import *

API_TOKEN = "8464698459:AAEiswJ5qaOJ7MMq2KDMdw7yE0m1icRyQt8"
WEBAPP_URL = "https://your-webapp-url.com"  # Replace with your deployed WebApp URL
CHANNEL_ID = "@yourchannel"  # Replace with your channel

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def get_markup():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Open Game", web_app=WebAppInfo(url=WEBAPP_URL))],
            [KeyboardButton(text="Leaderboard")],
            [KeyboardButton(text="Tasks"), KeyboardButton(text="Premium")],
        ], resize_keyboard=True
    )
    return markup

async def check_channel_member(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = await get_user(str(message.from_user.id)) or {}
    if not user:
        await set_user(str(message.from_user.id), {
            "username": message.from_user.username,
            "coins": 0,
            "premium": False,
            "stats": {"games": 0, "best_score": 0}
        })
    await message.answer("Welcome to 2048 Game!", reply_markup=get_markup())

@dp.message()
async def handle_message(message: types.Message):
    text = message.text.lower()
    user_id = str(message.from_user.id)
    if text == "leaderboard":
        leaderboard = await get_leaderboard() or {}
        top = sorted(leaderboard.values(), key=lambda u: -u['score'])[:10]
        msg = "Top 10:\n"
        for i, user in enumerate(top):
            msg += f"{i+1}. @{user['username']} - {user['score']} ({user.get('coins', 0)} coins)\n"
        await message.reply(msg)
    elif text == "tasks":
        tasks = await get_tasks() or {}
        msg = ""
        for section in ['daily', 'weekly', 'premium']:
            if section in tasks:
                msg += f"\n{section.capitalize()}:\n"
                for i, t in enumerate(tasks[section]):
                    msg += f" {i+1}. {t['name']} ({t['reward']} coins) [type: {t['type']}]\n"
        await message.reply(msg)
    elif text.startswith("/complete_task"):
        # /complete_task <section> <idx> [code]
        args = message.text.split()
        if len(args) < 3:
            await message.reply("Usage: /complete_task <section> <idx> [code]")
            return
        section, idx = args[1], int(args[2])-1
        code = args[3] if len(args) > 3 else None
        tasks = await get_tasks() or {}
        user = await get_user(user_id) or {}
        if section in tasks and 0 <= idx < len(tasks[section]):
            t = tasks[section][idx]
            if t["type"] == "subscribe":
                is_member = await check_channel_member(message.from_user.id)
                if not is_member:
                    await message.reply("Please join the channel to complete this task.")
                    return
            elif t["type"] == "code":
                if not code or code != "SECRET123":  # Example code, replace with actual logic
                    await message.reply("Invalid code.")
                    return
            # Mark task as completed if needed in user's data
            coins = user.get("coins", 0) + t["reward"]
            await set_user(user_id, {"coins": coins})
            await message.reply(f"Task completed! You earned {t['reward']} coins.")
        else:
            await message.reply("Task not found.")
    elif text == "premium":
        await message.reply("Send your premium code with /premium <code>")
    elif text.startswith("/premium"):
        code = message.text.split(" ", 1)[-1]
        if code == "PREMIUM2048":  # Example code
            await set_user(user_id, {"premium": True})
            await message.reply("Premium unlocked!")
        else:
            await message.reply("Invalid premium code.")
    # Admin commands
    elif text.startswith("/addtask"):
        # /addtask <section> <name> <reward> <type>
        try:
            _, section, name, reward, ttype = message.text.split(maxsplit=4)
            await admin_add_task(message, section, name, reward, ttype)
        except Exception as e:
            await message.reply("Usage: /addtask <section> <name> <reward> <type>")
    elif text.startswith("/edittask"):
        try:
            _, section, idx, name, reward, ttype = message.text.split(maxsplit=5)
            await admin_edit_task(message, section, int(idx)-1, name, reward, ttype)
        except Exception:
            await message.reply("Usage: /edittask <section> <idx> <name> <reward> <type>")
    elif text.startswith("/deltask"):
        try:
            _, section, idx = message.text.split(maxsplit=2)
            await admin_delete_task(message, section, int(idx)-1)
        except Exception:
            await message.reply("Usage: /deltask <section> <idx>")
    elif text.startswith("/leaderboard"):
        await admin_view_leaderboard(message)
    else:
        await message.reply("Unknown command.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))