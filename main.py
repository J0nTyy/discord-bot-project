import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import yt_dlp
import asyncio
from lyrics_command import LyricsCommand
from embedder import MusicEmbeds

load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix=".", intents=intents)

lyrics_obj = LyricsCommand(client)

voice_clients = {}
queues = {}

PLAY = "p"
PAUSE = "s"
RESUME = "c"
SKIP = "n"
QUEUE = "q"
CLEAR = "purge"
STOP = "l"

yt_dl_options = {
    "format": "m4a/bestaudio/best",
    "retries": 3,
    "no_playlist": True
}

ytdl = yt_dlp.YoutubeDL(yt_dl_options)

ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn -filter:a "volume=0.25"'}

async def play_next(ctx):
    if queues[ctx.guild.id]:
        next_item = queues[ctx.guild.id].pop(0)
        data = await asyncio.to_thread(ytdl.extract_info, next_item, download=False)

        if 'entries' in data:
            data = data['entries'][0]

        song = data['url']
        player = discord.FFmpegOpusAudio(song, **ffmpeg_options)

        voice_clients[ctx.guild.id].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))
        await MusicEmbeds.send_song_embed(ctx, data)

@client.event
async def on_ready():
    print(f'{client.user} is now jamming')

@client.command(name=PLAY)
async def play(ctx, *, url):
    if ctx.author.voice is None:
        await ctx.send("You need to be in a voice channel to play music!")
        return

    if ctx.guild.id not in voice_clients:
        voice_clients[ctx.guild.id] = await ctx.author.voice.channel.connect()
        queues[ctx.guild.id] = []

    if not url.startswith("http"):
        url = f"ytsearch:{url}"
        
    searching_message = await ctx.send("Looking for the song...")  # Inform the user that the bot is searching for the song

    data = await asyncio.to_thread(ytdl.extract_info, url, download=False)
    await searching_message.delete()
    
    if 'entries' in data:
        data = data['entries'][0]

    song = data['url']
    player = discord.FFmpegOpusAudio(song, **ffmpeg_options)

    if voice_clients[ctx.guild.id].is_playing():
        await ctx.send("Use `.queue` to add to queue!")
    else:
        voice_clients[ctx.guild.id].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))
        
        await MusicEmbeds.send_song_embed(ctx, data)

@client.command(name=QUEUE)
async def queue(ctx, *, search):
    if ctx.guild.id in queues:
        if not search.startswith("http"):
            search = f"ytsearch:{search}"
            
        searching_message = await ctx.send("Adding the song to the queue...")  # Inform the user that the bot is queuing the song

        queues[ctx.guild.id].append(search)
        data = await asyncio.to_thread(ytdl.extract_info, search, download=False)
        
        await searching_message.delete()  # Delete the searching message after the song is queued

        if 'entries' in data:
            data = data['entries'][0]

        await MusicEmbeds.send_song_embed(ctx, data)
    else:
        await ctx.send("There is no queue to add to!")

@client.command(name=CLEAR)
async def clear_queue(ctx):
    if ctx.guild.id in queues:
        queues[ctx.guild.id].clear()
        await ctx.send("Queue cleared!")
    else:
        await ctx.send("There is no queue to clear!")

@client.command(name=STOP)
async def stop(ctx):
    if ctx.guild.id in voice_clients:
        voice_clients[ctx.guild.id].stop()
        await voice_clients[ctx.guild.id].disconnect()
        del voice_clients[ctx.guild.id]
    else:
        await ctx.send("There is no song to stop!")

@client.command(name=SKIP)
async def skip(ctx):
    if ctx.guild.id in voice_clients:
        voice_clients[ctx.guild.id].stop()
        await play_next(ctx)
    else:
        await ctx.send("There is no song to skip!")

@client.command(name=PAUSE)
async def pause(ctx):
    if ctx.guild.id in voice_clients:
        voice_clients[ctx.guild.id].pause()
    else:
        await ctx.send("There is no song to pause!")

@client.command(name=RESUME)
async def resume(ctx):
    if ctx.guild.id in voice_clients:
        voice_clients[ctx.guild.id].resume()
    else:
        await ctx.send("There is no song to resume!")

@client.command(name="lyrics")
async def lyrics(ctx, *, arg):
    try:
        title, artist = arg.split(' - ')
        await lyrics_obj.send_lyrics(ctx, artist, title)

    except ValueError:
        await ctx.send("Please use the format `.lyrics <songname> - <artist>`.")

client.run(TOKEN)
