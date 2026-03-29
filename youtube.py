from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import os
import isodate

load_dotenv()
YOUTUBE_API = os.getenv('YOUTUBE_API')

# Build the YouTube service once and reuse it
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API)

# ──────────────────────────────────────────────
#  SEARCH
# ──────────────────────────────────────────────

def search_youtube(query, max_results=5):
    """Search YouTube and return a Discord-formatted string."""

    """
    Args:
        query: YouTube query sent to be searched
        max_results: max results outputed, default is 5
    """

    try:
        response = youtube.search().list(
            part='snippet',
            q=query,
            type='video',
            maxResults=max_results
        ).execute()

        if not response.get('items'):
            return '❌ No results found.'

        lines = [f'🔍 **Search results for:** `{query}`\n']
        for i, item in enumerate(response['items'], start=1):
            title   = item['snippet']['title']
            channel = item['snippet']['channelTitle']
            url     = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            lines.append(f'`{i}.` **{title}**\n    👤 {channel}\n    🔗 {url}')

        return '\n\n'.join(lines)

    except HttpError as e:
        return f'❌ Search error: {e}'

# ──────────────────────────────────────────────
#  CHANNEL
# ──────────────────────────────────────────────

def get_channel_stats(channel_id):
    """Fetch channel stats and return a Discord-formatted string."""

    """
    Args:
        channel_id: YouTube channel ID
    """

    try:
        response = youtube.channels().list(
            part='snippet,statistics',
            id=channel_id
        ).execute()

        if not response.get('items'):
            return f'❌ No channel found for ID: `{channel_id}`'

        item    = response['items'][0]
        stats   = item['statistics']
        snippet = item['snippet']

        title       = snippet['title']
        description = snippet.get('description', 'No description.')[:200]  # cap length
        subscribers = int(stats.get('subscriberCount', 0))
        views       = int(stats.get('viewCount', 0))
        video_count = int(stats.get('videoCount', 0))

        return (
                    f'# 📺 YouTube Channel\n'  # Header must start the line
                    f'──────────────────────────────────────────────\n'
                    f'## 📺 {title}\n'         # Header must start the line
                    f'─────────────────────\n'
                    f'👥 **Subscribers:** {subscribers:,}\n'
                    f'👁️  **Total Views:** {views:,}\n'
                    f'🎬 **Videos:** {video_count:,}\n'
                    f'─────────────────────\n'
                    f'📝 {description}\n'
                )

    except HttpError as e:
        return f'❌ Channel error: {e}'

# ──────────────────────────────────────────────
#  VIDEO
# ──────────────────────────────────────────────

def get_video_stats(video_id):
    """Fetch video stats and return a Discord-formatted string."""
    """
    Args:
        video_id: YouTube video ID
    """

    try:
        response = youtube.videos().list(
            part='snippet,statistics',
            id=video_id
        ).execute()

        if not response.get('items'):
            return f'❌ No video found for ID: `{video_id}`'

        item    = response['items'][0]
        stats   = item['statistics']
        snippet = item['snippet']

        title        = snippet['title']
        channel      = snippet.get('channelTitle', 'Unknown')
        published_at = snippet.get('publishedAt', '')[:10]  # just the date
        views        = int(stats.get('viewCount', 0))
        likes        = int(stats.get('likeCount', 0))
        comments     = int(stats.get('commentCount', 0))
        url          = f'https://www.youtube.com/watch?v={video_id}'

        return (
                    f'# 📺 YouTube Video\n'
                    f'──────────────────────────────────────────────\n'
                    f'## 🎬 {title}\n'
                    f'─────────────────────\n'
                    f'👤 **Channel:** {channel}\n'
                    f'📅 **Published:** {published_at}\n'
                    f'👁️  **Views:** {views:,}\n'
                    f'👍 **Likes:** {likes:,}\n'
                    f'💬 **Comments:** {comments:,}\n'
                    f'─────────────────────\n'
                    f'🔗 {url}\n'
                )

    except HttpError as e:
        return f'❌ Video error: {e}'

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

def format_playlist(playlist_id, show_videos=10):
    try:
        """
        Fetch a playlist and return a Discord-formatted string.

        Args:
            playlist_id: YouTube playlist ID
            show_videos: How many videos to list (default 10, use 0 for none)
        """
        playlist = get_playlist_stats(playlist_id)

        if playlist is None:
            return f'❌ No playlist found for ID: `{playlist_id}`'

        title       = playlist['title']
        channel     = playlist['channel']
        video_count = playlist['video_count']
        Total_Duration = playlist['Total Duration']
        
        lines = [
                    f'# 📺 YouTube Playlist',
                    f'──────────────────────────────────────────────\n'
                    f'## 📋 {title}',
                    f'─────────────────────',
                    f'👤 **Channel:** {channel}',
                    f'🎬 **Videos:** {video_count:,}',
                    f'⏱️ **Total Duration:** {Total_Duration}', # Added missing colon for consistency
                    f'─────────────────────',
                ]

        # List videos
        videos_to_show = playlist['videos'][:show_videos] if show_videos else []
        if videos_to_show:
            lines.append(f'**🎵 First {len(videos_to_show)} videos:**\n')
            for v in videos_to_show:
                num = v['position'] + 1
                lines.append(f'`{num:>3}.` [{v["title"]}]({v["url"]})')

            remaining = video_count - len(videos_to_show)
            if remaining > 0:
                lines.append(f'\n*...and {remaining} more videos*')

        return '\n'.join(lines)

    except HttpError as e:
        print(f'[playlist] formatting Error: {e}')
        return None