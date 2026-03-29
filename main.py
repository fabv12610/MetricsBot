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
    # Don't let the bot read its own messages
    if message.author == bot.user:
        return

    # Regex patterns for different YouTube link types
    
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
    "album": r"(?:https?:\/\/)?open\.spotify\.com\/album\/([a-zA-Z0-9]{22})",
    "artist": r"(?:https?:\/\/)?open\.spotify\.com\/artist\/([a-zA-Z0-9]{22})",
    "playlist": r"(?:https?:\/\/)?open\.spotify\.com\/playlist\/([a-zA-Z0-9]{22})",
    "podcast": r"(?:https?:\/\/)?open\.spotify\.com\/show\/([a-zA-Z0-9]{22})",
    "episode": r"(?:https?:\/\/)?open\.spotify\.com\/episode\/([a-zA-Z0-9]{22})",
    "user": r"(?:https?:\/\/)?open\.spotify\.com\/user\/([a-zA-Z0-9]{22})"
}

    SpotifyResults = {
        key: list(set(re.findall(pattern, message.content)))
        for key, pattern in SpotifyPatterns.items()
    }

    for _ in YoutubeResults['video']:
        await message.channel.send(youtube.get_video_stats(_))

    for _ in YoutubeResults['channel']:
        await message.channel.send(youtube.get_channel_stats(_))

    for _ in YoutubeResults['playlist']:
        await message.channel.send(youtube.format_playlist(_))
    
    for _ in SpotifyResults['track']:
        await message.channel.send(spotify.SpotifyTrack(_))

    #to run other commands
    await bot.process_commands(message)

try:
    bot.run(tokens, log_handler=handler, log_level=logging.DEBUG)
except Exception as e:
    print(e)