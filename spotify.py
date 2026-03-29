import discord
from spotapi import Public, Artist
from ast import literal_eval

def SpotifyTrack(song_id):
    try:
        song = Public.song_info(song_id)
        song_nested = song['data']['trackUnion']

        TrackName = song_nested['name']
        TrackDurationMS = song_nested['duration']['totalMilliseconds']
        TrackPlayCount = literal_eval(song_nested['playcount'])
        TrackArtist = song_nested['firstArtist']['items'][0]['profile']['name']

        # Optional data (safe access)
        TrackImage = song_nested.get('album', {}).get('coverArt', {}).get('sources', [{}])[0].get('url')
        TrackURL = song_nested.get('externalUrls', {}).get('spotify')

        # Duration
        duration_sec = TrackDurationMS // 1000
        minutes = duration_sec // 60
        seconds = duration_sec % 60

        embed = discord.Embed(
            title=f"🎵 {TrackName}",
            description="ᯤ Spotify Track",
            color=0x1DB954
        )

        if TrackURL:
            embed.url = TrackURL

        if TrackImage:
            embed.set_thumbnail(url=TrackImage)

        embed.add_field(name="👤 Artist", value=TrackArtist, inline=True)
        embed.add_field(name="⏱️ Duration", value=f"{minutes}:{seconds:02d}", inline=True)
        embed.add_field(name="🔥 Plays", value=f"{TrackPlayCount:,}", inline=True)

        embed.set_footer(text="Spotify • Track Info")

        return embed

    except Exception as e:
        return f"Error in SpotifyTrack: {e}"

def SpotifyArtist(artist_id):
    try:
        artist = Artist().get_artist(artist_id)
        artist_nested = artist['data']['artistUnion']
        
        ArtistName = artist_nested['profile']['name']
        ArtistFollowers = artist_nested['stats']['followers']
        ArtistMonthlyListeners = artist_nested['stats']['monthlyListeners']
        ArtistWorldRank = artist_nested['stats']['worldRank']

        top_city = artist_nested['stats']['topCities']['items'][0]
        ArtistTopCity = top_city['city']
        ArtistTopCountry = top_city['country']
        ArtistTopCityListeners = top_city['numberOfListeners']

        ArtistImage = artist_nested['visuals']['avatarImage']['sources'][0]['url']

        # Top tracks (limit 5)
        tracks = artist_nested['discography']['topTracks']['items'][:5]

        formatted_tracks = []
        for i, t in enumerate(tracks):
            name = t['track']['name']
            plays = literal_eval(t['track']['playcount'])
            ms = t['track']['duration']['totalMilliseconds']

            total_seconds = ms // 1000
            minutes, seconds = divmod(total_seconds, 60)

            formatted_tracks.append(
                f"**{i+1}. 🎵 {name}**\n⏱️ {minutes}:{seconds:02d} | 🔥 {plays:,}"
            )

        embed = discord.Embed(
            title=f"🎤 {ArtistName}",
            description="ᯤ Spotify Artist",
            color=0x1DB954
        )

        embed.set_thumbnail(url=ArtistImage)

        embed.add_field(
            name="📊 Stats",
            value=(
                f"👥 {ArtistFollowers:,} followers\n"
                f"🎧 {ArtistMonthlyListeners:,} monthly listeners\n"
                f"🌍 Rank #{ArtistWorldRank}"
            ),
            inline=False
        )

        embed.add_field(
            name="📍 Top Location",
            value=(
                f"{ArtistTopCity}, {ArtistTopCountry}\n"
                f"🎧 {ArtistTopCityListeners:,} listeners"
            ),
            inline=False
        )

        embed.add_field(
            name="🔥 Top Tracks",
            value="\n\n".join(formatted_tracks) or "No data available",
            inline=False
        )

        embed.set_footer(text="Spotify • Artist Overview")

        return embed

    except Exception as e:
        return f"Error in SpotifyArtist: {e}"