from Cherry.core.bot import Cherry
from Cherry.core.dir import StorageManager
from Cherry.core.userbot import Userbot
from Cherry.misc import dbb

from .logging import LOGGER

StorageManager()
dbb()

app = Cherry()
userbot = Userbot()


from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
