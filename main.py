import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import yt_dlp
import asyncio

load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix=".", intents=intents)

voice_clients = {}
queues = {}

yt_dl_options = {"format": "bestaudio/best"}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)

ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn -filter:a "volume=0.25"'}

async def send_song_embed(ctx, data):
    if 'entries' in data:
        info = data['entries'][0]
    else:
        info = data

    title = info.get('title')
    url = info.get('webpage_url')

    embed = discord.Embed(title="Now Playing" if ctx.command.name == "play" or ctx.command.name == "skip" else "Added to Queue",
                          description=f"[{title}]({url})", color=discord.Color.blue())
    embed.set_thumbnail(url=info.get('thumbnail'))
    await ctx.send(embed=embed)

async def play_next(ctx):
    if queues[ctx.guild.id]:
        next_item = queues[ctx.guild.id].pop(0)
        data = await asyncio.to_thread(ytdl.extract_info, next_item, download=False)

        if 'entries' in data:
            data = data['entries'][0]

        song = data['url']
        player = discord.FFmpegOpusAudio(song, **ffmpeg_options)

        voice_clients[ctx.guild.id].play(player, after=lambda e: asyncio.create_task(play_next(ctx)))
        await send_song_embed(ctx, data)

@client.event
async def on_ready():
    print(f'{client.user} is now jamming')

@client.command(name="play")
async def play(ctx, *, url):
    if ctx.author.voice is None:
        await ctx.send("You need to be in a voice channel to play music!")
        return

    if ctx.guild.id not in voice_clients:
        voice_clients[ctx.guild.id] = await ctx.author.voice.channel.connect()
        queues[ctx.guild.id] = []

    if not url.startswith("http"):
        url = f"ytsearch:{url}"

    data = await asyncio.to_thread(ytdl.extract_info, url, download=False)

    if 'entries' in data:
        data = data['entries'][0]

    song = data['url']
    player = discord.FFmpegOpusAudio(song, **ffmpeg_options)

    if voice_clients[ctx.guild.id].is_playing():
        ctx.send("Song added to queue!")
    else:
        voice_clients[ctx.guild.id].play(player, after=lambda e: asyncio.create_task(play_next(ctx)))
        await send_song_embed(ctx, data)

@client.command(name="queue")
async def queue(ctx, *, search):
    if ctx.guild.id in queues:
        if not search.startswith("http"):
            search = f"ytsearch:{search}"
        queues[ctx.guild.id].append(search)
        data = await asyncio.to_thread(ytdl.extract_info, search, download=False)

        if 'entries' in data:
            data = data['entries'][0]

        await send_song_embed(ctx, data)
    else:
        await ctx.send("There is no queue to add to!")

@client.command(name="clear_queue")
async def clear_queue(ctx):
    if ctx.guild.id in queues:
        queues[ctx.guild.id].clear()
        await ctx.send("Queue cleared!")
    else:
        await ctx.send("There is no queue to clear!")

@client.command(name="stop")
async def stop(ctx):
    if ctx.guild.id in voice_clients:
        voice_clients[ctx.guild.id].stop()
        await voice_clients[ctx.guild.id].disconnect()
        del voice_clients[ctx.guild.id]
    else:
        await ctx.send("There is no song to stop!")

@client.command(name="skip")
async def skip(ctx):
    if ctx.guild.id in voice_clients:
        voice_clients[ctx.guild.id].stop()
        await play_next(ctx)
    else:
        await ctx.send("There is no song to skip!")

@client.command(name="pause")
async def pause(ctx):
    if ctx.guild.id in voice_clients:
        voice_clients[ctx.guild.id].pause()
    else:
        await ctx.send("There is no song to pause!")

@client.command(name="resume")
async def resume(ctx):
    if ctx.guild.id in voice_clients:
        voice_clients[ctx.guild.id].resume()
    else:
        await ctx.send("There is no song to resume!")

client.run(TOKEN)
