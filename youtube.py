from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import os
import isodate
import discord
import re

load_dotenv()
YOUTUBE_API = os.getenv('YOUTUBE_API')

# Build the YouTube service once and reuse it
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API)

# ──────────────────────────────────────────────
#  SEARCH
# ──────────────────────────────────────────────

def search_youtube(query, max_results=5):
    try:
        response = youtube.search().list(
            part='snippet',
            q=query,
            type='video',
            maxResults=max_results
        ).execute()

        if not response.get('items'):
            return discord.Embed(
                title="❌ No results",
                description=f"No results for `{query}`",
                color=0xFF0000
            )

        lines = []
        for i, item in enumerate(response['items'], start=1):
            title   = item['snippet']['title']
            channel = item['snippet']['channelTitle']
            url     = f"https://www.youtube.com/watch?v={item['id']['videoId']}"

            lines.append(f"**{i}. [{title}]({url})**\n👤 {channel}")

        embed = discord.Embed(
            title=f"🔍 {query}",
            description="\n\n".join(lines),
            color=0xFF0000
        )

        embed.set_footer(text="YouTube • Search")

        return embed

    except HttpError as e:
        return discord.Embed(title="❌ Error", description=str(e), color=0xFF0000)

# ──────────────────────────────────────────────
#  CHANNEL
# ──────────────────────────────────────────────

def get_channel_stats(channel_id):
    try:
        response = youtube.channels().list(
            part='snippet,statistics',
            id=channel_id
        ).execute()

        if not response.get('items'):
            return discord.Embed(
                title="❌ Not found",
                description=f"Channel ID `{channel_id}`",
                color=0xFF0000
            )

        item    = response['items'][0]
        stats   = item['statistics']
        snippet = item['snippet']

        title       = snippet['title']
        description = snippet.get('description', 'No description.')[:200]
        subscribers = int(stats.get('subscriberCount', 0))
        views       = int(stats.get('viewCount', 0))
        video_count = int(stats.get('videoCount', 0))
        thumbnail   = snippet.get('thumbnails', {}).get('high', {}).get('url')

        embed = discord.Embed(
            title=f"📺 {title}",
            description=description,
            color=0xFF0000
        )

        if thumbnail:
            embed.set_thumbnail(url=thumbnail)

        embed.add_field(
            name="📊 Stats",
            value=(
                f"👥 {subscribers:,} subscribers\n"
                f"👁️ {views:,} views\n"
                f"🎬 {video_count:,} videos"
            ),
            inline=False
        )

        embed.set_footer(text="YouTube • Channel")

        return embed

    except HttpError as e:
        return discord.Embed(title="❌ Error", description=str(e), color=0xFF0000)

# ──────────────────────────────────────────────
#  VIDEO
# ──────────────────────────────────────────────

def get_video_stats(video_id):
    try:
        response = youtube.videos().list(
            part='snippet,statistics',
            id=video_id
        ).execute()

        if not response.get('items'):
            return discord.Embed(
                title="❌ Not found",
                description=f"Video ID `{video_id}`",
                color=0xFF0000
            )

        item    = response['items'][0]
        stats   = item['statistics']
        snippet = item['snippet']

        title   = snippet['title']
        channel = snippet.get('channelTitle', 'Unknown')
        date    = snippet.get('publishedAt', '')[:10]
        views   = int(stats.get('viewCount', 0))
        likes   = int(stats.get('likeCount', 0))
        comments= int(stats.get('commentCount', 0))
        url     = f'https://www.youtube.com/watch?v={video_id}'
        thumb   = snippet.get('thumbnails', {}).get('high', {}).get('url')

        embed = discord.Embed(
            title=f"🎬 {title}",
            url=url,
            color=0xFF0000
        )

        if thumb:
            embed.set_thumbnail(url=thumb)

        embed.add_field(name="👤 Channel", value=channel, inline=True)
        embed.add_field(name="📅 Published", value=date, inline=True)

        embed.add_field(
            name="📊 Stats",
            value=(
                f"👁️ {views:,}\n"
                f"👍 {likes:,}\n"
                f"💬 {comments:,}"
            ),
            inline=False
        )

        embed.set_footer(text="YouTube • Video")

        return embed

    except HttpError as e:
        return discord.Embed(title="❌ Error", description=str(e), color=0xFF0000)

# ──────────────────────────────────────────────
#  PLAYLIST
# ──────────────────────────────────────────────

def get_playlist_stats(playlist_id):
    """Fetch playlist stats and return a Discord-formatted string."""

    """
    Args:
        playlist_id: YouTube playlist ID
    """

    try:
        # ─── Get playlist metadata ───
        playlist_response = youtube.playlists().list(
            part='snippet,contentDetails',
            id=playlist_id
        ).execute()

        if not playlist_response.get('items'):
            return None

        item = playlist_response['items'][0]
        snippet = item['snippet']

        playlist = {
            'title': snippet['title'],
            'description': snippet.get('description', ''),
            'channel': snippet.get('channelTitle', ''),
            'video_count': int(item['contentDetails'].get('itemCount', 0)),
            'videos': [],
        }

        # ─── Get all videos ───
        next_page = None
        video_id_list = []

        while True:
            items_response = youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page
            ).execute()

            for entry in items_response.get('items', []):
                s = entry['snippet']

                if s.get('title') in ('Deleted video', 'Private video'):
                    continue

                vid = s['resourceId']['videoId']
                video_id_list.append(vid)

                playlist['videos'].append({
                    'title': s['title'],
                    'video_id': vid,
                    'url': f"https://www.youtube.com/watch?v={vid}",
                    'position': s['position'],
                })

            next_page = items_response.get('nextPageToken')
            if not next_page:
                break

        # ─── Calculate total duration (batched) ───
        total_seconds = 0

        for i in range(0, len(video_id_list), 50):
            batch = video_id_list[i:i+50]

            res = youtube.videos().list(
                part='contentDetails',
                id=','.join(batch)
            ).execute()

            for v in res['items']:
                dur = v['contentDetails']['duration']
                total_seconds += isodate.parse_duration(dur).total_seconds()

        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)

        playlist['Total Duration'] = f"{hours}:{minutes:02}:{seconds:02}"

        return playlist

    except HttpError as e:
        print(f'[playlist] Error: {e}')
        return None

# ──────────────────────────────────────────────
#  FORMAT PLAYLIST
# ──────────────────────────────────────────────

def format_playlist(playlist_id, show_videos=5):
    try:
        playlist = get_playlist_stats(playlist_id)

        if playlist is None:
            return discord.Embed(
                title="❌ Not found",
                description=f"Playlist ID `{playlist_id}`",
                color=0xFF0000
            )

        title       = playlist['title']
        channel     = playlist['channel']
        video_count = playlist['video_count']
        duration    = playlist['Total Duration']

        videos = playlist['videos'][:show_videos]

        video_list = "\n".join(
            f"**{i+1}. [{v['title']}]({v['url']})**"
            for i, v in enumerate(videos)
        )

        embed = discord.Embed(
            title=f"📋 {title}",
            description=f"👤 {channel}",
            color=0xFF0000
        )

        embed.add_field(
            name="📊 Info",
            value=(
                f"🎬 {video_count:,} videos\n"
                f"⏱️ {duration}"
            ),
            inline=False
        )

        if videos:
            embed.add_field(
                name="🎵 Videos",
                value=video_list,
                inline=False
            )

        embed.set_footer(text="YouTube • Playlist")

        return embed

    except HttpError as e:
        return discord.Embed(title="❌ Error", description=str(e), color=0xFF0000)