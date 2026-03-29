from spotapi import Public
from ast import literal_eval

# ──────────────────────────────────────────────
#  Track
# ──────────────────────────────────────────────

def SpotifyTrack(song_id):

    try:

        """
        Fetch a Spotify playlist and return a Discord-formatted string.

        Args:
            song_id: Spotify song id in url. 5knuzwU65gJK7IF5yJsuaW in https://open.spotify.com/track/5knuzwU65gJK7IF5yJsuaW

        """

        song = Public.song_info(song_id)
        song_nested = song['data']['trackUnion']

        TrackName = song_nested['name']
        TrackDurationMS = song_nested['duration']['totalMilliseconds']
        TrackPlayCount = literal_eval(song_nested['playcount'])
        TrackArtist = song_nested['firstArtist']['items'][0]['profile']['name']

        duration_sec = TrackDurationMS // 1000
        minutes = duration_sec // 60
        seconds = duration_sec % 60

        return (
            f'──────────────────────────────────────────────\n'
            f'# ᯤ Spotify Track\n'
            f'──────────────────────────────────────────────\n'
            f"## 🎵 {TrackName}\n"
            f'─────────────────────\n'
            f"👤 **Artist:** {TrackArtist}\n"
            f"⏱️ **Duration:** {minutes}:{seconds:02d}\n"
            f"🔥 **Plays:** {TrackPlayCount:,}"
        )
    except:
        return 'Error has occured, please try again'