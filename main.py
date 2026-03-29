import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from googleapiclient.discovery import build
import re
import youtube
import spotify

load_dotenv()
tokens = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    YoutubePatterns = {
        "video": r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})",
        "channel": r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/(?:channel\/|c\/|user\/|@)([a-zA-Z0-9_.-]+)",
        "playlist": r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/.*[?&]list=([a-zA-Z0-9_-]+)"
    }

    YoutubeResults = {
        key: list(set(re.findall(pattern, message.content)))
        for key, pattern in YoutubePatterns.items()
    }

    SpotifyPatterns = {
        "track": r"(?:https?:\/\/)?open\.spotify\.com\/track\/([a-zA-Z0-9]{22})",
        "artist": r"(?:https?:\/\/)?open\.spotify\.com\/artist\/([a-zA-Z0-9]{22})",
    }

    SpotifyResults = {
        key: list(set(re.findall(pattern, message.content)))
        for key, pattern in SpotifyPatterns.items()
    }

    # helper (handles embed OR string)
    async def send_result(result):
        if isinstance(result, discord.Embed):
            await message.channel.send(embed=result)
        else:
            await message.channel.send(result)

    # ─── YouTube ───
    for _ in YoutubeResults['video'][:1]:
        await send_result(youtube.get_video_stats(_))

    for _ in YoutubeResults['channel'][:1]:
        await send_result(youtube.get_channel_stats(_))

    for _ in YoutubeResults['playlist'][:1]:
        await send_result(youtube.format_playlist(_))

    # ─── Spotify ───
    for _ in SpotifyResults['track'][:1]:
        await send_result(spotify.SpotifyTrack(_))

    for _ in SpotifyResults['artist'][:1]:
        await send_result(spotify.SpotifyArtist(_))

    # ✅ ALWAYS at the end
    await bot.process_commands(message)

try:
    bot.run(tokens, log_handler=handler, log_level=logging.DEBUG)
except Exception as e:
    print(e)