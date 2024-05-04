# lyrics_provider.py
from azapi import AZlyrics

class LyricsProvider:
    def __init__(self):
        self.az_api = AZlyrics()

    def get_lyrics(self, artist, title):
        try:
            self.az_api.artist = artist
            self.az_api.title = title
            self.az_api.getLyrics(save=False)
            lyrics = self.az_api.lyrics
            return lyrics
        except Exception as e:
            print(f"An error occurred while fetching lyrics: {e}")
            return None