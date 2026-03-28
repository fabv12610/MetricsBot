from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import os
import isodate

load_dotenv()
YOUTUBE_API = os.getenv('YOUTUBE_API')

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API)

def get_playlist_stats(playlist_id):
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

        #playlist['Total Duration'] = f"{hours}:{minutes:02}:{seconds:02}"

        return playlist

    except HttpError as e:
        print(f'[playlist] Error: {e}')
        return None


print(get_playlist_stats('PLK8eO9itnhzdBaYl-QtVMFzagf4Aa4FmF'))