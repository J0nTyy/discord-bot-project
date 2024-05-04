# lyrics_command.py
import lyricsgenius

class LyricsCommand:
    def __init__(self, client):
        self.client = client
        self.genius = lyricsgenius.Genius()

    async def send_lyrics(self, ctx, artist, title):
        try:
            await ctx.send(f"Fetching lyrics for {title.capitalize()} by {artist.capitalize()} ...")
            artist_variable = self.genius.search_artist(artist, max_songs=3, sort="title", include_features=True)

            song = self.genius.search_song(title, artist_variable.name)
            lyrics = song.lyrics
            lyrics_lines = lyrics.split('\n')

            if lyrics_lines:
                lyrics_without_first_line = '\n'.join(lyrics_lines[1:])
                for chunk in [lyrics_without_first_line[i:i+2000] for i in range(0, len(lyrics_without_first_line), 2000)]:
                    await ctx.send(chunk)
                    
        except Exception as e:
            await ctx.send("An error occurred while fetching lyrics.")
            print(f"An error occurred: {e}")