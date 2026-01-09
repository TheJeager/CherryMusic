import asyncio
import os
import re
import time
import uuid
from dataclasses import dataclass
from typing import Optional, Tuple, List, Dict, Union, TypedDict

from yt_dlp import YoutubeDL
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch

try:
    import config
except Exception:
    config = None

from Cherry.utils.database import is_on_off
from Cherry.utils.formatters import time_to_seconds


@dataclass(frozen=True)
class Paths:
    cookies_dir: str = getattr(config, "COOKIES_DIR", "cookies")
    downloads_dir: str = getattr(config, "DOWNLOADS_DIR", "downloads")


PATHS = Paths()


def ensure_dir(path: str) -> None:
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def safe_cookiefile() -> Optional[str]:
    ensure_dir(PATHS.cookies_dir)
    try:
        cookies_files = [f for f in os.listdir(PATHS.cookies_dir) if f.endswith(".txt")]
        if not cookies_files:
            return None
        return os.path.join(PATHS.cookies_dir, cookies_files[0])
    except Exception:
        return None


async def shell_cmd(cmd: str) -> str:
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, err = await proc.communicate()
    if err:
        err_text = err.decode("utf-8", errors="ignore")
        if "unavailable videos are hidden" in err_text.lower():
            return out.decode("utf-8", errors="ignore")
        return err_text
    return out.decode("utf-8", errors="ignore")


class FormatInfo(TypedDict, total=False):
    format: str
    filesize: Optional[int]
    format_id: str
    ext: str
    format_note: Optional[str]
    yturl: str
    cookiefile: Optional[str]


class TrackDetails(TypedDict, total=False):
    title: str
    link: str
    vidid: str
    duration_min: Optional[str]
    thumb: str
    cookiefile: Optional[str]


class YouTubeAPI:
    def __init__(self) -> None:
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|

\[[0-?]*[ -/]*[@-~])")
        ensure_dir(PATHS.downloads_dir)

    async def exists(self, link: str, videoid: Union[bool, str] = None) -> bool:
        if videoid:
            link = self.base + str(videoid)
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Optional[str]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        for message in messages:
            text = message.text or message.caption or ""
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        offset, length = entity.offset, entity.length
                        if offset is not None and length is not None:
                            return text[offset: offset + length]
            if message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    def _normalize_link(self, link: str, videoid: Union[bool, str] = None) -> str:
        if videoid:
            link = self.base + str(videoid)
        if "&" in link:
            link = link.split("&")[0]
        return link

    async def _search_single(self, link: str) -> Optional[Dict]:
        try:
            results = VideosSearch(link, limit=1)
            payload = await results.next()
            items = payload.get("result") or []
            return items[0] if items else None
        except Exception:
            return None

    async def details(self, link: str, videoid: Union[bool, str] = None) -> Tuple[str, Optional[str], int, str, str]:
        link = self._normalize_link(link, videoid)
        result = await self._search_single(link)
        if not result:
            raise ValueError("No results found")
        title = result.get("title", "Unknown Title")
        duration_min = result.get("duration")
        thumbnail = (result.get("thumbnails") or [{}])[0].get("url", "").split("?")[0]
        vidid = result.get("id", "")
        duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None) -> str:
        link = self._normalize_link(link, videoid)
        result = await self._search_single(link)
        if not result:
            raise ValueError("No results found")
        return result.get("title", "Unknown Title")

    async def duration(self, link: str, videoid: Union[bool, str] = None) -> Optional[str]:
        link = self._normalize_link(link, videoid)
        result = await self._search_single(link)
        if not result:
            return None
        return result.get("duration")

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None) -> Optional[str]:
        link = self._normalize_link(link, videoid)
        result = await self._search_single(link)
        if not result:
            return None
        return (result.get("thumbnails") or [{}])[0].get("url", "").split("?")[0]

    async def video(self, link: str, videoid: Union[bool, str] = None) -> Tuple[int, str]:
        link = self._normalize_link(link, videoid)
        args = ["yt-dlp", "-g", "-f", "best[height<=?720][width<=?1280]", link]
        cookie = safe_cookiefile()
        if cookie:
            args[1:1] = ["--cookies", cookie]
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stdout:
            url = stdout.decode().split("\n")[0].strip()
            return 1, url
        return 0, stderr.decode()

    async def playlist(self, link: str, limit: int, user_id: Union[int, str], videoid: Union[bool, str] = None) -> List[str]:
        link = self._normalize_link(link, videoid)
        cmd = (
            f"yt-dlp -i --compat-options no-youtube-unavailable-videos "
            f"--get-id --flat-playlist --playlist-end {limit} --skip-download '{link}' "
            f"2>/dev/null"
        )
        playlist = await shell_cmd(cmd)
        try:
            return [key for key in playlist.split("\n") if key.strip()]
        except Exception:
            return []

    async def track(self, link: str, videoid: Union[bool, str] = None) -> Tuple[TrackDetails, str]:
        link = self._normalize_link(link, videoid)
        result = await self._search_single(link)
        if not result:
            raise ValueError("No results found")
        title = result.get("title", "Unknown Title")
        duration_min = result.get("duration")
        vidid = result.get("id", "")
        yturl = result.get("link", link)
        thumbnail = (result.get("thumbnails") or [{}])[0].get("url", "").split("?")[0]
        track_details: TrackDetails = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
            "cookiefile": safe_cookiefile(),
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None) -> Tuple[List[FormatInfo], str]:
        link = self._normalize_link(link, videoid)
        ytdl_opts = {"quiet": True}
        ydl = YoutubeDL(ytdl_opts)
        formats_available: List[FormatInfo] = []
        info = ydl.extract_info(link, download=False)
        for fmt in info.get("formats", []):
            fmt_str = str(fmt.get("format", ""))
            if "dash" in fmt_str.lower():
                continue
            format_id = fmt.get("format_id")
            ext = fmt.get("ext")
            if not format_id or not ext:
                continue
            formats_available.append(
                {
                    "format": fmt_str,
                    "filesize": fmt.get("filesize"),
                    "format_id": format_id,
                    "ext": ext,
                    "format_note": fmt.get("format_note"),
                    "yturl": link,
                    "cookiefile": safe_cookiefile(),
                }
            )
        return
