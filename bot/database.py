import aiohttp

FIREBASE_URL = "https://project-3020568111544941346-default-rtdb.firebaseio.com"

async def get_user(uid):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{FIREBASE_URL}/users/{uid}.json") as resp:
            return await resp.json()

async def set_user(uid, data):
    async with aiohttp.ClientSession() as session:
        async with session.patch(f"{FIREBASE_URL}/users/{uid}.json", json=data) as resp:
            return await resp.json()

async def get_tasks():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{FIREBASE_URL}/tasks.json") as resp:
            return await resp.json()

async def set_tasks(tasks):
    async with aiohttp.ClientSession() as session:
        async with session.put(f"{FIREBASE_URL}/tasks.json", json=tasks) as resp:
            return await resp.json()

async def get_leaderboard():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{FIREBASE_URL}/leaderboard.json") as resp:
            return await resp.json()

async def add_to_leaderboard(uid, username, score, coins):
    async with aiohttp.ClientSession() as session:
        data = {"uid": uid, "username": username, "score": score, "coins": coins}
        async with session.post(f"{FIREBASE_URL}/leaderboard.json", json=data) as resp:
            return await resp.json()