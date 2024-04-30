from discord.ext import commands
from dotenv import load_dotenv
import discord
import asyncio
import yt_dlp
import urllib.parse


TOKEN = "MTIzNDgwOTgxNDE5OTE3NzMwNw.GTp_iq.f7mV2bzRCe-4ZRv4ySRMPxEUNwIjQpp1oDq-P8"
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix=".", intents=intents)

voice_clients = {}
queues = {}
yt_dl_options = {"format": "bestaudio/best"}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)

ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}

@client.event
async def on_ready():
    print(f'{client.user} is now jamming')

async def play_next(ctx):
    if queues[ctx.guild.id]:
        # Fetch the first item in the queue
        next_item = queues[ctx.guild.id].pop(0)
        # Play the next item, whether it's a direct link or a search term
        await play(ctx, search=next_item)
        
async def send_song_embed(ctx, data):
    if 'entries' in data:
        info = data['entries'][0]
    else:
        info = data

    title = info.get('title')
    url = info.get('webpage_url')

    embed = discord.Embed(title="Now Playing" if ctx.command.name == "play" else "Added to Queue", description=f"[{title}]({url})", color=discord.Color.blue())
    embed.set_thumbnail(url=info.get('thumbnail'))
    await ctx.send(embed=embed)

def is_url(string):
    parsed = urllib.parse.urlparse(string)
    return bool(parsed.scheme and parsed.netloc)

@client.command(name="play")
async def play(ctx, *, search):
    try:
        if ctx.author.voice is None:
            return await ctx.send("Get in a voice channel first...")

        voice_client = await ctx.author.voice.channel.connect()
        voice_clients[ctx.guild.id] = voice_client
    except Exception as e:
        print(e)

    try:
        loop = asyncio.get_event_loop()
        
        # Check if `search` is a URL, if not, prepend 'ytsearch:' to search on YouTube
        if not is_url(search):
            search = f"ytsearch:{search}"

        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(search, download=False))
        
        if 'entries' in data:  # if a playlist or search result is returned, take the first song
            data = data['entries'][0]
        
        song = data['url']
        player = discord.FFmpegOpusAudio(song, **ffmpeg_options)

        voice_clients[ctx.guild.id].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))
        await send_song_embed(ctx, data)
    except Exception as e:
        print(e)

@client.command(name="clear_queue")
async def clear_queue(ctx):
    if ctx.guild.id in queues:
        queues[ctx.guild.id].clear()
        await ctx.send("Queue cleared!")
    else:
        await ctx.send("There is no queue to clear!")

@client.command(name="pause")
async def pause(ctx):
    try:
        voice_clients[ctx.guild.id].pause()
    except Exception as e:
        print(e)

@client.command(name="resume")
async def resume(ctx):
    try:
        voice_clients[ctx.guild.id].resume()
    except Exception as e:
        print(e)

@client.command(name="stop")
async def stop(ctx):
    try:
        voice_clients[ctx.guild.id].stop()
        await voice_clients[ctx.guild.id].disconnect()
        del voice_clients[ctx.guild.id]
    except Exception as e:
        print(e)

@client.command(name="queue")
async def queue(ctx, *, search):
    loop = asyncio.get_event_loop()
    # Check if `search` is a URL, if not, prepend 'ytsearch:' to search on YouTube
    if not is_url(search):
        search = f"ytsearch:{search}"
    
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(search, download=False))
    
    if 'entries' in data:  # if a playlist or search result is returned, take the first song
        data = data['entries'][0]
    
    song = data['url']
    # Add to queue
    if ctx.guild.id not in queues:
        queues[ctx.guild.id] = []
    queues[ctx.guild.id].append(song)
    await send_song_embed(ctx, data)
    
    
@client.command(name="skip")
async def skip(ctx):
    guild_id = ctx.guild.id
    voice_client = voice_clients.get(guild_id)

    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("Skipped the current song.")
        await play_next(ctx)
    else:
        await ctx.send("No song is currently playing.")

client.run(TOKEN)