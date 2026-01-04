import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# Get this value from my.telegram.org
API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")

# Get your token from @BotFather on Telegram.
BOT_TOKEN = getenv("BOT_TOKEN")

# Get your mongo url from cloud.mongodb.com
MONGO_DB_URI = getenv("MONGO_DB_URI")

DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 60))

# Chat id of a group
LOGGER_ID = int(getenv("LOGGER_ID"))

# Get this value from @MissRose_bot on Telegram by /id
OWNER_ID = int(getenv("OWNER_ID", 0))

WEBSITE = getenv("WEBSITE", "https://vercel.app")

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/UpdateChannel")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/SupportChat")

# Set this to True if you want the assistant to automatically leave chats after an interval
AUTO_LEAVING_ASSISTANT = bool(getenv("AUTO_LEAVING_ASSISTANT", False))


# Get this credentials from https://developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", None)
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", None)


# Maximum limit for fetching playlist's track from youtube, spotify, apple links.
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))

#Debug
DEBUG_IGNORE_LOG = True

# Telegram audio and video file size limit (in bytes)
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", 104857600))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", 1073741824))
# Checkout https://www.gbmb.org/mb-to-bytes for converting mb to bytes


# Get your pyrogram v2 session from @StringFatherBot on Telegram
STRING1 = getenv("STRING_SESSION", None)
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)


BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}

# Cookies URL - here
COOKIES = ("https://batbin.me/")

# For - downloads
DOWNLOADS_DIR = "downloads"

START_IMG_URL = ("https://files.catbox.moe/4a09b9.jpg")
PING_IMG_URL = ("https://files.catbox.moe/prt763.jpg")
PLAYLIST_IMG_URL = ("https://files.catbox.moe/2w7jsz.jpg")
STATS_IMG_URL = ("https://files.catbox.moe/09m524.jpg")
TELEGRAM_AUDIO_URL = ("https://files.catbox.moe/2w7jsz.jpg")
TELEGRAM_VIDEO_URL = ("https://files.catbox.moe/2w7jsz.jpg")
STREAM_IMG_URL = ("https://files.catbox.moe/2w7jsz.jpg")
SOUNCLOUD_IMG_URL = ("https://files.catbox.moe/2w7jsz.jpg")
YOUTUBE_IMG_URL = ("https://files.catbox.moe/2w7jsz.jpg")
SPOTIFY_ARTIST_IMG_URL = ("https://files.catbox.moe/2w7jsz.jpg")
SPOTIFY_ALBUM_IMG_URL = ("https://files.catbox.moe/2w7jsz.jpg")
SPOTIFY_PLAYLIST_IMG_URL = ("https://files.catbox.moe/2w7jsz.jpg")


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))


if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHANNEL url is wrong. Please ensure that it starts with https://"
        )

if SUPPORT_CHAT:
    if not re.match("(?:http|https)://", SUPPORT_CHAT):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHAT url is wrong. Please ensure that it starts with https://"
        )
