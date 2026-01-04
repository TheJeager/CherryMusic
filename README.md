# Cherry Music Bot

<p align="center">
  <img src="https://files.catbox.moe/prt763.jpg" width="420" alt="Cherry Music Bot">
</p>

<p align="center">
  <b>Fast · Elegant · Multi-platform</b>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-3670A0?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/pytgcalls/pytgcalls"><img src="https://img.shields.io/badge/PyTgCalls-audio--calls-FF6B6B?style=flat-square&logo=github&logoColor=white" alt="PyTgCalls"></a>
  <a href="https://www.mongodb.com/"><img src="https://img.shields.io/badge/MongoDB-Atlas-47A248?style=flat-square&logo=mongodb&logoColor=white" alt="MongoDB"></a>
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-ready-2496ed?style=flat-square&logo=docker&logoColor=white" alt="Docker"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-000000?style=flat-square&logo=opensourceinitiative&logoColor=white" alt="License"></a>
</p>

---

# About Cherry

Cherry is a sleek, high-performance Telegram music bot built for modern communities. It provides fast search and streaming from major platforms — Spotify, Resso, Apple Music, Carbon and YouTube — directly into Telegram voice chats with low latency and smooth playback.
---

# Key Features

- Multi-platform search and streaming: Spotify, Resso, Apple Music, Carbon, YouTube  
- Persistent queues and per-user playlists using MongoDB  
- Playback controls: play, pause, resume, skip, stop, seek, loop  
- Lightweight, low-latency streaming powered by PyTgCalls / NtgCalls  
- Admin-friendly controls and inline support for instant interaction

---

# Commands List

| Command | Description |
|--------:|:------------|
| /play [song | url] | Play a track or add to queue |
| /queue | Show current queue |
| /playlist | Manage your saved playlists |
| /pause / /resume | Pause or resume playback |
| /skip / /stop | Skip current track or stop playback |
| /seek [mm:ss] | Seek within current track |
| /loop [none|single|all] | Toggle loop mode |
| /help | Full command list |

(Exact command names may vary — check `/help` on your running bot.)

---

# Tech Stack

- Python 3.10+  
- [Pyrogram](https://docs.pyrogram.org/) — Telegram client  
- [PyTgCalls](https://github.com/pytgcalls/pytgcalls) (and optional NtgCalls compatibility) — voice streaming  
- MongoDB — persistence for queues & playlists  
- FFmpeg — audio/video processing

---

# Required Environment Variables

Create a `.env` (or set host env vars) with:

- BOT_TOKEN — Telegram bot token from @BotFather  
- API_ID — Telegram API ID (my.telegram.org)  
- API_HASH — Telegram API Hash (my.telegram.org)  
- MONGO_DB_URL — MongoDB connection string (mongodb+srv://...)  
- STRING_SESSION — Get your pyrogram v2 session from @StringFatherBot on Telegram 
- OWNER_ID — Telegram user id for owner/admin   
- LOGGER_ID — optional Telegram group id for logs

---

# Deploy Options

- Heroku: set config vars and use a Procfile  
- Docker: build with the included Dockerfile and run with --env-file .env  
- VPS: run inside a virtualenv or container with systemd/supervisor

If you want, I can add a compact Dockerfile, Procfile and a one-click Heroku template.

---

# Troubleshooting

- Bot offline: verify BOT_TOKEN, API_ID, API_HASH are correct and check logs.  
- Playback errors: confirm FFmpeg availability and PyTgCalls compatibility; check the bot logs for stack traces.  
- Search or metadata issues: ensure optional API credentials (Spotify, etc.) are present if you rely on third-party lookups.
