from pyrogram import filters
from pyrogram.types import Message

from Cherry import app
from Cherry.core.call import Cherry

WELCOME_GROUP = 20
CLOSE_GROUP = 30


@app.on_message(filters.video_chat_started, group=WELCOME_GROUP)
@app.on_message(filters.video_chat_ended, group=CLOSE_GROUP)
async def watcher(_, message: Message):
    try:
        await Cherry.force_stop_stream(message.chat.id)
    except Exception:
        pass