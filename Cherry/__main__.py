import asyncio
import importlib

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from Cherry import LOGGER, app, userbot
from Cherry.core.call import Cherry
from Cherry.misc import sudo
from Cherry.plugins import ALL_MODULES
from Cherry.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS
from Cherry.core.cookies import save_cookies


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("👤 Assistant client variables not defined, exiting...")
        exit()
    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass
    await Cherry.start()
    await save_cookies()
    for all_module in ALL_MODULES:
        importlib.import_module("Cherry.plugins" + all_module)
    LOGGER("Cherry.plugins").info("🧺 Successfully Imported Modules...")
    await userbot.start()
    await app.start()
    try:
        await Cherry.stream_call("https://files.catbox.moe/vmg5fj.mp4")
    except NoActiveGroupCall:
        LOGGER("Cherry").error(
            "🔌 Please turn on the videochat of your log group\channel.\n\nStopping Bot..."
        )
        exit()
    except:
        pass
    await Cherry.decorators()
    LOGGER("Cherry").info(
    "Bot Started"
)
    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("Cherry").info("🚫 Stopping Cherry Music Bot...")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
