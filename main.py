import discord
from discord.ext import commands
import youtube_dl
import os

client = commands.Bot(command_prefix="^",intents=discord.Intents.all())
ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}


@client.event
async def on_ready():
    print("David is ready")

@client.command(pass_context= True)
async def join(ctx):
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()
        await ctx.send(f"I have joined {channel}")
    else:
        await ctx.send("You are not in a voice channel.")

@client.command(pass_context= True)
async def leave(ctx):
    if (ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.send("I left the channel")
    else:
        await ctx.send("I am not in a voice channel.")

@client.command(pass_context = True)
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients,guild = ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        ctx.send("No song is playing at this moment.")

@client.command(pass_context = True)
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients,guild = ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        ctx.send("No song is paused at this moment.")

@client.command(pass_context = True)
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients,guild = ctx.guild)
    if voice.is_playing() or voice.is_paused():
        voice.stop()
    else:
        ctx.send("No song is playing at this moment.")

@client.command(pass_context=True)
async def play(ctx, arg):
    # Check if the user is in a voice channel
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)

        # Check if the bot is already in a voice channel
        if voice_client is None:
            voice_client = await channel.connect()
        else:
            await voice_client.move_to(channel)
            if voice_client.is_playing():
                await ctx.send("A song is already playing please wait for it to finish and try again.")
            else:
                # Download audio from the YouTube video
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                }

                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(arg, download=False)
                    url = info['formats'][0]['url']

                # Play audio
                voice_client.play(discord.FFmpegOpusAudio(url, **ffmpeg_options), after=lambda e: print('done', e))
                await ctx.send('Now playing: ' + info['title'])
    else:
        await ctx.send("You need to be in a voice channel to use this command.")

client.run(os.environ.get("token"))
