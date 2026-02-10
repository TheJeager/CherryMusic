import asyncio
import os
import re
import json
import logging
from typing import Union, Optional, Dict, Tuple
from pathlib import Path

from yt_dlp import YoutubeDL
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch

import config
from Cherry.utils.database import is_on_off
from Cherry.utils.formatters import time_to_seconds

# Setup logging
logger = logging.getLogger(__name__)


def get_cookies_file() -> Optional[str]:
    """
    Get cookies file path if available.
    Searches for .txt files in cookies directory.
    Returns None if no cookies file found.
    """
    try:
        cookie_dir = "cookies"
        if not os.path.exists(cookie_dir):
            logger.warning(f"Cookies directory '{cookie_dir}' not found")
            return None
        
        cookies_files = [f for f in os.listdir(cookie_dir) if f.endswith(".txt")]
        
        if not cookies_files:
            logger.warning(f"No cookie files found in '{cookie_dir}'")
            return None
        
        cookie_path = os.path.join(cookie_dir, cookies_files[0])
        logger.info(f"Using cookies file: {cookie_path}")
        return cookie_path
    except Exception as e:
        logger.error(f"Error getting cookies file: {e}")
        return None


async def shell_cmd(cmd: str) -> str:
    """
    Execute shell command asynchronously.
    Handles both stdout and stderr appropriately.
    """
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, errorz = await proc.communicate()
        
        if errorz:
            error_text = errorz.decode("utf-8", errors="ignore").lower()
            # Handle specific expected errors
            if "unavailable videos are hidden" in error_text:
                return out.decode("utf-8", errors="ignore")
            else:
                logger.warning(f"Shell command error: {errorz.decode('utf-8', errors='ignore')}")
                return errorz.decode("utf-8", errors="ignore")
        
        return out.decode("utf-8", errors="ignore")
    except Exception as e:
        logger.error(f"Error executing shell command: {e}")
        return f"Error: {str(e)}"


class YouTubeAPI:
    """
    YouTube API handler with support for both cookie-based and cookie-less methods.
    Handles video fetching, streaming, and playlist support.
    """
    
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        self.cookies_file = get_cookies_file()
        self.use_cookies = self.cookies_file is not None

    def _get_ydl_opts(self, with_cookies: bool = True) -> Dict:
        """
        Get yt-dlp options based on whether cookies are available.
        
        Args:
            with_cookies: Use cookies if available
            
        Returns:
            Dictionary with yt-dlp options
        """
        base_opts = {
            'quiet': False,
            'no_warnings': False,
            'extract_flat': 'in_playlist',
            'socket_timeout': 30,
            'retries': 5,
            'fragment_retries': 5,
        }
        
        # Add cookies if available and requested
        if with_cookies and self.cookies_file:
            base_opts['cookiefile'] = self.cookies_file
            logger.info("Using cookies for YouTube request")
        else:
            logger.info("Making YouTube request without cookies")
        
        return base_opts

    async def exists(self, link: str, videoid: Union[bool, str] = None) -> bool:
        """
        Check if a link is a valid YouTube URL.
        
        Args:
            link: URL or video ID
            videoid: If True, treat link as video ID
            
        Returns:
            Boolean indicating if link is valid YouTube URL
        """
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        """
        Extract YouTube URL from message.
        
        Args:
            message_1: Pyrogram Message object
            
        Returns:
            Extracted URL or None
        """
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        
        text = ""
        offset = None
        length = None
        
        for message in messages:
            if offset:
                break
            
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        
        return None if offset in (None,) else text[offset : offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None) -> Tuple[str, str, int, str, str]:
        """
        Get video details (title, duration, thumbnail, ID).
        Tries with cookies first, falls back to without cookies if needed.
        
        Args:
            link: YouTube URL or video ID
            videoid: If True, treat link as video ID
            
        Returns:
            Tuple of (title, duration_min, duration_sec, thumbnail, videoid)
        """
        if videoid:
            link = self.base + link
        
        if "&" in link:
            link = link.split("&")[0]
        
        try:
            results = VideosSearch(link, limit=1)
            result_data = await results.next()
            
            if not result_data.get("result"):
                logger.warning(f"No results found for: {link}")
                return None
            
            for result in result_data["result"]:
                title = result.get("title", "Unknown")
                duration_min = result.get("duration", "0")
                thumbnail = result.get("thumbnails", [{}])[0].get("url", "").split("?")[0]
                vidid = result.get("id", "")
                
                if str(duration_min) == "None" or not duration_min:
                    duration_sec = 0
                else:
                    duration_sec = int(time_to_seconds(duration_min))
                
                return title, duration_min, duration_sec, thumbnail, vidid
        
        except Exception as e:
            logger.error(f"Error fetching video details: {e}")
            return None

    async def title(self, link: str, videoid: Union[bool, str] = None) -> str:
        """
        Get video title.
        
        Args:
            link: YouTube URL or video ID
            videoid: If True, treat link as video ID
            
        Returns:
            Video title or "Unknown"
        """
        if videoid:
            link = self.base + link
        
        if "&" in link:
            link = link.split("&")[0]
        
        try:
            results = VideosSearch(link, limit=1)
            result_data = await results.next()
            
            if result_data.get("result"):
                return result_data["result"][0].get("title", "Unknown")
        except Exception as e:
            logger.error(f"Error fetching title: {e}")
        
        return "Unknown"

    async def fetch_stream_url(self, link: str, use_cookies: bool = True) -> Optional[str]:
        """
        Fetch direct stream URL using yt-dlp.
        Tries with cookies first, then falls back to without cookies.
        
        Args:
            link: YouTube URL or video ID
            use_cookies: Try with cookies first
            
        Returns:
            Direct stream URL or None if failed
        """
        attempts = []
        
        # First attempt: with cookies (if available)
        if use_cookies and self.cookies_file:
            attempts.append(('with_cookies', True))
        
        # Second attempt: without cookies
        attempts.append(('without_cookies', False))
        
        for attempt_name, with_cookies in attempts:
            try:
                logger.info(f"Attempting to fetch stream URL ({attempt_name}): {link}")
                
                opts = self._get_ydl_opts(with_cookies=with_cookies)
                opts.update({
                    'format': 'bestaudio/best',
                    'quiet': True,
                    'no_warnings': True,
                })
                
                with YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(link, download=False)
                    
                    if 'url' in info:
                        logger.info(f"Successfully fetched stream URL ({attempt_name})")
                        return info['url']
                    elif 'entries' in info:
                        # Handle playlists
                        for entry in info['entries']:
                            if entry and 'url' in entry:
                                logger.info(f"Successfully fetched stream URL from playlist ({attempt_name})")
                                return entry['url']
            
            except Exception as e:
                logger.warning(f"Failed to fetch stream URL ({attempt_name}): {e}")
                continue
        
        logger.error(f"Could not fetch stream URL for: {link}")
        return None

    async def get_audio_url(self, link: str) -> Optional[str]:
        """
        Get audio URL with automatic fallback mechanism.
        
        Args:
            link: YouTube URL or video ID
            
        Returns:
            Audio stream URL or None
        """
        return await self.fetch_stream_url(link, use_cookies=True)

    async def verify_stream(self, url: str, timeout: int = 10) -> bool:
        """
        Verify if stream URL is still valid.
        
        Args:
            url: Stream URL to verify
            timeout: Timeout in seconds
            
        Returns:
            Boolean indicating if stream is accessible
        """
        try:
            cmd = f'ffprobe -v error -select_streams a:0 -show_entries stream=codec_type -of csv=p=0 "{url}" -timeout {timeout * 1000000}'
            result = await shell_cmd(cmd)
            return "audio" in result.lower() or len(result) > 0
        except Exception as e:
            logger.error(f"Error verifying stream: {e}")
            return False

    async def get_playlist_videos(self, playlist_url: str) -> Optional[list]:
        """
        Extract videos from a playlist.
        
        Args:
            playlist_url: YouTube playlist URL
            
        Returns:
            List of video information or None
        """
        try:
            opts = self._get_ydl_opts(with_cookies=self.use_cookies)
            opts.update({
                'extract_flat': True,
                'quiet': True,
            })
            
            with YoutubeDL(opts) as ydl:
                info = ydl.extract_info(playlist_url, download=False)
                
                if 'entries' in info:
                    videos = []
                    for entry in info['entries']:
                        if entry:
                            videos.append({
                                'id': entry.get('id'),
                                'title': entry.get('title'),
                                'url': self.base + entry.get('id') if entry.get('id') else None
                            })
                    return videos
        
        except Exception as e:
            logger.error(f"Error fetching playlist videos: {e}")
        
        return None


class YouTubeDownloader:
    """
    Handles downloading and converting YouTube audio to formats suitable for streaming.
    """
    
    def __init__(self):
        self.youtube_api = YouTubeAPI()
        self.temp_dir = "downloads"
        
        # Create temp directory if it doesn't exist
        Path(self.temp_dir).mkdir(exist_ok=True)

    async def download_audio(self, link: str, output_file: Optional[str] = None) -> Optional[str]:
        """
        Download audio from YouTube in MP3 format.
        
        Args:
            link: YouTube URL
            output_file: Custom output file path
            
        Returns:
            Path to downloaded audio file or None
        """
        if not output_file:
            # Generate unique filename
            video_id = link.split('v=')[-1].split('&')[0]
            output_file = os.path.join(self.temp_dir, f"{video_id}.mp3")
        
        try:
            logger.info(f"Downloading audio from: {link}")
            
            opts = self.youtube_api._get_ydl_opts(with_cookies=self.youtube_api.use_cookies)
            opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': output_file.replace('.mp3', ''),
                'quiet': False,
            })
            
            with YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=True)
                logger.info(f"Successfully downloaded: {output_file}")
                return output_file
        
        except Exception as e:
            logger.error(f"Error downloading audio: {e}")
            return None

    async def cleanup_temp(self):
        """Clean up temporary downloaded files."""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info("Cleaned up temporary files")
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")
