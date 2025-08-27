from aiogram import types
from .database import set_tasks, get_tasks, get_user, set_user, get_leaderboard

ADMIN_USERNAME = "H08_09"

async def is_admin(username):
    return username == ADMIN_USERNAME

async def admin_add_task(message: types.Message, section, name, reward, ttype):
    if not await is_admin(message.from_user.username):
        await message.reply("You are not admin!")
        return
    tasks = await get_tasks() or {}
    if section not in tasks:
        tasks[section] = []
    tasks[section].append({"name": name, "reward": int(reward), "type": ttype})
    await set_tasks(tasks)
    await message.reply(f"Task added to {section}: {name} [{reward} coins, type: {ttype}]")

async def admin_edit_task(message: types.Message, section, idx, name, reward, ttype):
    if not await is_admin(message.from_user.username):
        await message.reply("You are not admin!")
        return
    tasks = await get_tasks() or {}
    if section in tasks and 0 <= idx < len(tasks[section]):
        tasks[section][idx] = {"name": name, "reward": int(reward), "type": ttype}
        await set_tasks(tasks)
        await message.reply("Task edited.")
    else:
        await message.reply("Task not found.")

async def admin_delete_task(message: types.Message, section, idx):
    if not await is_admin(message.from_user.username):
        await message.reply("You are not admin!")
        return
    tasks = await get_tasks() or {}
    if section in tasks and 0 <= idx < len(tasks[section]):
        tasks[section].pop(idx)
        await set_tasks(tasks)
        await message.reply("Task deleted.")
    else:
        await message.reply("Task not found.")

async def admin_manage_user(message: types.Message, username, coins=None, premium=None):
    # Simple user management by username
    pass

async def admin_view_leaderboard(message: types.Message):
    leaderboard = await get_leaderboard()
    text = "Leaderboard:\n"
    top = sorted(leaderboard.values(), key=lambda u: -u['score'])[:10]
    for i, user in enumerate(top):
        text += f"{i+1}. @{user['username']} - {user['score']} ({user.get('coins', 0)} coins)\n"
    await message.reply(text)