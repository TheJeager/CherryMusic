import platform
from sys import version as pyver

import psutil
from pyrogram import __version__ as pyrover
from pyrogram import filters
from pyrogram.errors import MessageIdInvalid
from pyrogram.types import InputMediaPhoto, Message
from pytgcalls.__version__ import __version__ as pytgver

import config
from Cherry import app
from Cherry.core.userbot import assistants
from Cherry.misc import mongodb
from Cherry.plugins import ALL_MODULES
from Cherry.utils.database import (
    get_served_chats,
    get_served_users,
    get_sudoers,
)
from Cherry.utils.decorators.language import language, languageCB
from Cherry.utils.inline.stats import back_stats_buttons, stats_buttons
from config import BANNED_USERS, OWNER_ID


@app.on_message(filters.command(["stats", "gstats"]) & filters.group & ~BANNED_USERS)
@language
async def stats_global(client, message: Message, _):
    if message.from_user.id != OWNER_ID:
        return await message.reply_text(
            "❌ access denied."
        )

    upl = stats_buttons(_, True)
    await message.reply_photo(
        photo=config.STATS_IMG_URL,
        caption=_["gstats_2"].format(app.mention),
        reply_markup=upl,
    )


@app.on_callback_query(filters.regex("stats_back") & ~BANNED_USERS)
@languageCB
async def home_stats(client, CallbackQuery, _):
    if CallbackQuery.from_user.id != OWNER_ID:
        return await CallbackQuery.answer(
            "❌ access denied",
            show_alert=True,
        )

    upl = stats_buttons(_, True)
    await CallbackQuery.edit_message_text(
        text=_["gstats_2"].format(app.mention),
        reply_markup=upl,
    )


@app.on_callback_query(filters.regex("TopOverall") & ~BANNED_USERS)
@languageCB
async def overall_stats(client, CallbackQuery, _):
    if CallbackQuery.from_user.id != OWNER_ID:
        return await CallbackQuery.answer(
            "❌ access denied",
            show_alert=True,
        )

    upl = back_stats_buttons(_)
    await CallbackQuery.edit_message_text(_["gstats_1"].format(app.mention))

    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())

    text = _["gstats_3"].format(
        app.mention,
        len(assistants),
        len(BANNED_USERS),
        served_chats,
        served_users,
        len(ALL_MODULES),
        1,
        config.AUTO_LEAVING_ASSISTANT,
        config.DURATION_LIMIT_MIN,
    )

    med = InputMediaPhoto(media=config.STATS_IMG_URL, caption=text)
    try:
        await CallbackQuery.edit_message_media(media=med, reply_markup=upl)
    except MessageIdInvalid:
        await CallbackQuery.message.reply_photo(
            photo=config.STATS_IMG_URL,
            caption=text,
            reply_markup=upl,
        )


@app.on_callback_query(filters.regex("bot_stats_sudo"))
@languageCB
async def bot_stats(client, CallbackQuery, _):
    if CallbackQuery.from_user.id != OWNER_ID:
        return await CallbackQuery.answer(
            "❌ access denied",
            show_alert=True,
        )

    upl = back_stats_buttons(_)
    await CallbackQuery.edit_message_text(_["gstats_1"].format(app.mention))

    p_core = psutil.cpu_count(logical=False)
    t_core = psutil.cpu_count(logical=True)
    ram = str(round(psutil.virtual_memory().total / (1024.0**3))) + " GB"

    try:
        cpu_freq = psutil.cpu_freq().current
        cpu_freq = (
            f"{round(cpu_freq / 1000, 2)}GHz"
            if cpu_freq >= 1000
            else f"{round(cpu_freq, 2)}MHz"
        )
    except:
        cpu_freq = "N/A"

    hdd = psutil.disk_usage("/")
    call = await mongodb.command("dbstats")

    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())

    text = _["gstats_5"].format(
        app.mention,
        len(ALL_MODULES),
        platform.system(),
        ram,
        p_core,
        t_core,
        cpu_freq,
        pyver.split()[0],
        pyrover,
        pytgver,
        str(hdd.total / (1024**3))[:4],
        str(hdd.used / (1024**3))[:4],
        str(hdd.free / (1024**3))[:4],
        served_chats,
        served_users,
        len(BANNED_USERS),
        1,
        str(call["dataSize"] / 1024)[:6],
        call["storageSize"] / 1024,
        call["collections"],
        call["objects"],
    )

    med = InputMediaPhoto(media=config.STATS_IMG_URL, caption=text)
    try:
        await CallbackQuery.edit_message_media(media=med, reply_markup=upl)
    except MessageIdInvalid:
        await CallbackQuery.message.reply_photo(
            photo=config.STATS_IMG_URL,
            caption=text,
            reply_markup=upl,
        )