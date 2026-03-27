import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from googleapiclient.discovery import build
import re
import youtube
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
    # 1. Videos (Matches watch?v=, youtu.be/, shorts/, and embeds -> extracts 11-char ID)
    video_pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    
    # 2. Channels (Matches /channel/ID, /c/name, /user/name, or @handle -> extracts the ID/handle)
    channel_pattern = r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/(?:channel\/|c\/|user\/|@)([a-zA-Z0-9_.-]+)"
    
    # 3. Playlists (Matches any youtube URL containing list= -> extracts the playlist ID)
    playlist_pattern = r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/.*[?&]list=([a-zA-Z0-9_-]+)"

    # Extract all matches found in the user's message
    video_ids = re.findall(video_pattern, message.content)
    channel_ids = re.findall(channel_pattern, message.content)
    playlist_ids = re.findall(playlist_pattern, message.content)

    # remove duplicates
    video_list = list(set(video_ids))
    channel_list = list(set(channel_ids))
    playlist_list = list(set(playlist_ids))

    for _ in (video_list):
        await message.channel.send(youtube.get_video_stats(_))

    for _ in (channel_list):
        await message.channel.send(youtube.get_channel_stats(_))

    for _ in (playlist_list):
        await message.channel.send(youtube.format_playlist(_))

    # IMPORTANT: Allow commands (like !help or other bot commands) to run
    await bot.process_commands(message)

try:
    bot.run(tokens, log_handler=handler, log_level=logging.DEBUG)
except Exception as e:
    print(e)