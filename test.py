from lyrics_command import LyricsProvider

lyrics_provider = LyricsProvider()

lyrics = lyrics_provider.get_lyrics("Shape of You")
print(lyrics)