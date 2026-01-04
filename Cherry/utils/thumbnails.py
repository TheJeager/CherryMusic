import os
import re
import aiofiles
import aiohttp
import logging
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from py_yt import VideosSearch
from config import YOUTUBE_IMG_URL
from Cherry import app

# Logging Setup
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Directories
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# Layout Constants
PANEL_W, PANEL_H = 800, 600
PANEL_X = (1280 - PANEL_W) // 2
PANEL_Y = 50
TRANSPARENCY = 180
INNER_OFFSET = 40

THUMB_W, THUMB_H = 600, 300
THUMB_X = PANEL_X + (PANEL_W - THUMB_W) // 2
THUMB_Y = PANEL_Y + INNER_OFFSET

TITLE_X = THUMB_X
META_X = THUMB_X
TITLE_Y = THUMB_Y + THUMB_H + 20
META_Y = TITLE_Y + 50

BAR_X, BAR_Y = THUMB_X, META_Y + 40
BAR_RED_LEN = 300
BAR_TOTAL_LEN = 600

ICONS_W, ICONS_H = 450, 60
ICONS_X = PANEL_X + (PANEL_W - ICONS_W) // 2
ICONS_Y = BAR_Y + 60

MAX_TITLE_WIDTH = PANEL_W - 100


def trim_to_width(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> str:
    ellipsis = "…"
    text = text[:50]  # Limit title to 50 characters
    if font.getlength(text) <= max_w:
        return text
    for i in range(len(text) - 1, 0, -1):
        if font.getlength(text[:i] + ellipsis) <= max_w:
            return text[:i] + ellipsis
    return ellipsis


async def get_thumb(videoid: str) -> str:
    cache_path = os.path.join(CACHE_DIR, f"{videoid}_v5.png")
    if os.path.exists(cache_path):
        return cache_path

    try:
        results = VideosSearch(f"https://www.youtube.com/watch?v={videoid}", limit=1)
        results_data = await results.next()
        data = results_data["result"][0]
        title = re.sub(r"\W+", " ", data.get("title", "Unsupported Title")).title()
        thumbnail = data.get("thumbnails", [{}])[0].get("url", YOUTUBE_IMG_URL)
        duration = data.get("duration")
        views = data.get("viewCount", {}).get("short", "Unknown Views")
    except Exception as e:
        logging.error(f"Error fetching YouTube data: {e}")
        title, thumbnail, duration, views = "Unsupported Title", YOUTUBE_IMG_URL, None, "Unknown Views"

    is_live = not duration or str(duration).strip().lower() in {"", "live", "live now"}
    duration_text = "🔴 LIVE" if is_live else duration or "Unknown Mins"

    thumb_path = os.path.join(CACHE_DIR, f"thumb_{videoid}.jpg")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    async with aiofiles.open(thumb_path, "wb") as f:
                        await f.write(await resp.read())
                else:
                    logging.error(f"Failed to download thumbnail (HTTP {resp.status})")
                    return YOUTUBE_IMG_URL
    except Exception as e:
        logging.error(f"Download error: {e}")
        return YOUTUBE_IMG_URL

    try:
        base = Image.open(thumb_path).resize((1280, 720)).convert("RGBA")
        bg = ImageEnhance.Brightness(base.filter(ImageFilter.GaussianBlur(15))).enhance(0.5)
    except Exception as e:
        logging.error(f"Image processing error: {e}")
        return YOUTUBE_IMG_URL

    # Frosted Gradient Panel
    try:
        panel_area = bg.crop((PANEL_X, PANEL_Y, PANEL_X + PANEL_W, PANEL_Y + PANEL_H))
        gradient = Image.new("RGBA", (PANEL_W, PANEL_H), color=0)
        for y in range(PANEL_H):
            r = 255
            g = 255 - int((y / PANEL_H) * 80)
            b = 255 - int((y / PANEL_H) * 120)
            a = TRANSPARENCY
            for x in range(PANEL_W):
                gradient.putpixel((x, y), (r, g, b, a))
        frosted = Image.alpha_composite(panel_area, gradient)
        mask = Image.new("L", (PANEL_W, PANEL_H), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, PANEL_W, PANEL_H), 35, fill=255)
        bg.paste(frosted, (PANEL_X, PANEL_Y), mask)
    except Exception as e:
        logging.error(f"Panel error: {e}")

    # Thumbnail with Border
    try:
        thumb = ImageOps.fit(base, (THUMB_W, THUMB_H), method=Image.Resampling.LANCZOS)
        tmask = Image.new("L", thumb.size, 0)
        ImageDraw.Draw(tmask).rounded_rectangle((0, 0, THUMB_W, THUMB_H), 25, fill=255)

        border = Image.new("RGBA", (THUMB_W + 10, THUMB_H + 10), (0, 0, 0, 0))
        bmask = Image.new("L", (THUMB_W + 10, THUMB_H + 10), 0)
        ImageDraw.Draw(bmask).rounded_rectangle((0, 0, THUMB_W + 10, THUMB_H + 10), 30, fill=255)

        bg.paste(border, (THUMB_X - 5, THUMB_Y - 5), bmask)
        bg.paste(thumb, (THUMB_X, THUMB_Y), tmask)
    except Exception as e:
        logging.error(f"Thumbnail error: {e}")

    try:
        title_font = ImageFont.truetype("Cherry/assets/font2.ttf", 30)
        meta_font = ImageFont.truetype("Cherry/assets/font.ttf", 22)
        draw = ImageDraw.Draw(bg)

        title_text = trim_to_width(title, title_font, MAX_TITLE_WIDTH)
        draw.text((TITLE_X, TITLE_Y), title_text, fill="white", font=title_font)

        draw.text((META_X, META_Y), f"YouTube | {views}           Player : @{app.username}", fill="#FF0000", font=meta_font)

        if is_live:
            live_font = ImageFont.truetype("Cherry/assets/font2.ttf", 22)
            draw.ellipse((META_X + 200, META_Y - 5, META_X + 225, META_Y + 20), fill=(255, 0, 0, 255))
            draw.text((META_X + 230, META_Y), "LIVE", fill="red", font=live_font)
    except Exception as e:
        logging.error(f"Text rendering error: {e}")

    # Progress Bar
    try:
        draw.line([(BAR_X, BAR_Y), (BAR_X + BAR_RED_LEN, BAR_Y)], fill="#FF0000", width=10)
        draw.ellipse([(BAR_X - 5, BAR_Y - 5), (BAR_X + 5, BAR_Y + 5)], fill="#FF0000")
        draw.line([(BAR_X + BAR_RED_LEN, BAR_Y), (BAR_X + BAR_TOTAL_LEN, BAR_Y)], fill="#555555", width=6)
        draw.ellipse([(BAR_X + BAR_TOTAL_LEN - 5, BAR_Y - 5), (BAR_X + BAR_TOTAL_LEN + 5, BAR_Y + 5)], fill="#555555")

        draw.text((BAR_X, BAR_Y + 20), "00:00", fill="white", font=meta_font)
        draw.text((BAR_X + BAR_TOTAL_LEN - 100, BAR_Y + 20), duration_text,
                  fill="#FF0000" if is_live else "white", font=meta_font)
    except Exception as e:
        logging.error(f"Progress bar error: {e}")

    # Icons
    try:
        icons_path = "Cherry/assets/play_icons.png"
        if os.path.isfile(icons_path):
            icons = Image.open(icons_path).resize((ICONS_W, ICONS_H)).convert("RGBA")
        else:
            icons = Image.new("RGBA", (ICONS_W, ICONS_H), (0, 0, 0, 0))
            d = ImageDraw.Draw(icons)
            d.polygon([(20, 10), (20, 50), (60, 30)], fill="white")
        bg.paste(icons, (ICONS_X, ICONS_Y), icons)
    except Exception as e:
        logging.error(f"Icons error: {e}")

    # Save and Cleanup
    try:
        os.remove(thumb_path)
    except Exception as e:
        logging.error(f"Cleanup error: {e}")

    try:
        bg.save(cache_path, quality=95)
        return cache_path
    except Exception as e:
        logging.error(f"Save error: {e}")
        return YOUTUBE_IMG_URL
