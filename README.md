# Discord Bot Project

This project is a Discord bot designed to provide music playback functionality within Discord servers.

## Features

- Play music from YouTube via URL or search query.
- Pause, resume, and skip tracks.
- Queue management with the ability to clear the current queue.
- Automatic playback of the next item in the queue.
- Send lyrics of a track in discord as a message.

## Setup

1. Clone the repository to your local machine.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Create a `.env` file at the root of the project and add your Discord bot token like this: 
   TOKEN=your_discord_bot_token_here
4. You'll need to download FFmpeg and add it to PATH for the bot to actually play music in discord. Watch this video for a tutorial:
   https://www.youtube.com/watch?v=4jx2_j5Seew&ab_channel=Tricknology

6. Run the bot with `python main.py`.

## Commands

- `.play <URL or search term>` - Play music or add to queue.
- `.pause` - Pause the current song.
- `.resume` - Resume the paused song.
- `.skip` - Skip the current song.
- `.stop` - Stop the music and disconnect the bot.
- `.clear` - Clear the current music queue.
- `.queue <search term>` - Add a song to the queue.
- `.lyrics` - To send a message with the lyrics of a song.
  
## Dependencies

- discord.py
- yt-dlp
- FFmpeg
