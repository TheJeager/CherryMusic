import os
import sys
import traceback
from io import StringIO
from time import time

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from Cherry import app
from config import OWNER_ID


async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message):\n"
        + "\n".join(f"    {i}" for i in code.split("\n")),
        {},
        locals(),
    )
    return await locals()["__aexec"](client, message)


async def edit_or_reply(msg: Message, text: str, **kwargs):
    if msg.from_user and msg.from_user.is_self:
        return await msg.edit_text(text, **kwargs)
    return await msg.reply_text(text, **kwargs)


@app.on_message(
    filters.command("eval")
    & filters.user(OWNER_ID)
    & ~filters.forwarded
    & ~filters.via_bot
)
async def eval_executor(client: app, message: Message):
    if len(message.command) < 2:
        return await edit_or_reply(message, "<b>What do you want me to execute?</b>")

    code = message.text.split(None, 1)[1]
    start = time()

    old_stdout, old_stderr = sys.stdout, sys.stderr
    stdout, stderr = StringIO(), StringIO()
    sys.stdout, sys.stderr = stdout, stderr

    exc = None
    try:
        await aexec(code, client, message)
    except Exception:
        exc = traceback.format_exc()

    sys.stdout, sys.stderr = old_stdout, old_stderr

    result = exc or stderr.getvalue() or stdout.getvalue() or "Success"
    runtime = round(time() - start, 3)

    output = f"<b>⥤ RESULT:</b>\n<pre language='python'>{result}</pre>"

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⏳ Runtime", callback_data=f"runtime|{runtime}"),
                InlineKeyboardButton("🗑 Close", callback_data=f"close|{message.from_user.id}"),
            ]
        ]
    )

    if len(output) > 4096:
        filename = "eval_output.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result)

        await message.reply_document(
            filename,
            caption=f"<b>⥤ EVAL:</b>\n<code>{code[:1000]}</code>",
            reply_markup=keyboard,
            quote=False,
        )
        os.remove(filename)
        await message.delete()
    else:
        await edit_or_reply(message, output, reply_markup=keyboard)


@app.on_callback_query(filters.regex(r"^runtime\|"))
async def runtime_callback(_, cq: CallbackQuery):
    await cq.answer(f"Runtime: {cq.data.split('|', 1)[1]} sec", show_alert=True)


@app.on_callback_query(filters.regex(r"^close\|"))
async def close_callback(_, cq: CallbackQuery):
    user_id = int(cq.data.split("|", 1)[1])
    if cq.from_user.id != user_id:
        return await cq.answer("Not allowed.", show_alert=True)
    await cq.message.delete()
    await cq.answer()
