# embedder.py
import discord

class MusicEmbeds:
    @staticmethod
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