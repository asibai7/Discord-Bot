import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions
from discord.utils import get
import requests
import json
from apikeys import *

#enables all intents so bot has permission
intents = discord.Intents.all() 
intents.members = True
#creates a bot instance with a command prefix
client = commands.Bot(command_prefix = '!',intents=intents)

queues = {}
def check_queue(ctx, id):
    if queues[id]:
        voice = ctx.guild.voice_client
        source = queues[id].pop(0)
        voice.play(source, after=lambda x=None: check_queue(ctx, id))

#event listener for when bot connects to the Discord server
@client.event
async def on_ready():
    #setting bot status to idle, if removed then bot defaults to online
    await client.change_presence(status=discord.Status.idle, activity=discord.Activity(type = discord.ActivityType.listening, name="21 Savage whilst doing Bot things"))
    print("The bot is Online")
    print("-----------------")

#command definition for !hello
@client.command()
async def hello(ctx):
    await ctx.send("Hello, I am the bot")

#event listener for when a member joins the server
@client.event
async def on_member_join(member):
    jokeurl = "https://joke3.p.rapidapi.com/v1/joke"

    headers = {
        "x-rapidapi-key": JokeApi,
        "x-rapidapi-host": "joke3.p.rapidapi.com"
    }

    response = requests.get(jokeurl, headers=headers)
    joke = response.json()['content']
    channel = client.get_channel(1259530305501528107)
    await channel.send("Welcome to the server, here is a joke:")
    await channel.send(joke)

#event listener for when a member leaves the server
@client.event
async def on_member_remove(member):
    channel = client.get_channel(1259530305501528107)
    await channel.send("Goodbye")

#command for bot to join voice
@client.command(pass_context = True)
async def join(ctx):
    #if user is in voice channel
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()
        await ctx.send("I've joined the voice channel!")
    else:
        await ctx.send("You aren't in a voice channel, you must be in a voice channel to run this command!")

#command for bot to leave voice
@client.command(pass_context = True)
async def leave(ctx):
    #if bot is in voice channel
    if (ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.send("I've left the voice channel")
    else:
        await ctx.send("I am not in a voice channel!")

#command for bot to pause audio
@client.command(pass_context = True)
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("No audio is playing!")

#command for bot to resume playing audio
@client.command(pass_context = True)
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("No audio is paused!")

#command for bot to stop playing audio
@client.command(pass_context = True)
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()

#command for bot to play audio
@client.command(pass_context = True)
async def play(ctx, arg):
    try:
        voice = ctx.guild.voice_client
        audio = arg + '.mp3'
        source = FFmpegPCMAudio(audio)
        player = voice.play(source, after=lambda x=None : check_queue(ctx, ctx.message.guild.id)) #check for queued audio files after current audio file ends
    except AttributeError:
        await ctx.send("I am not in a voice channel!")

#command for bot to queue audio files
@client.command(pass_context = True)
async def queue(ctx, arg):
    try:
        voice = ctx.guild.voice_client
        audio = arg + '.mp3'
        source = FFmpegPCMAudio(audio)
        guild_id = ctx.message.guild.id #gets discord server id
        if guild_id in queues:
            queues[guild_id].append(source)
        else:
            queues[guild_id] = [source]
        await ctx.send("Added to queue!")
    except AttributeError:
        await ctx.send("I am not in a voice channel!")

# Command for bot to skip current audio file
@client.command(pass_context=True)
async def skip(ctx):
    voice = ctx.guild.voice_client
    if voice and voice.is_playing():
        voice.stop()
        await ctx.send("Skipped the current audio!")
    else:
        await ctx.send("No audio is playing!")

#event which enables bot to listen to all messages and detect certain words
@client.event
async def on_message(message):
    if message.content == "Tampa, Florida":
        await message.delete()
        await message.channel.send("Dont leak my address!")
    elif message.content == "Ahmad Sibai":
        await message.delete()
        await message.channel.send("Dont expose my full name!")
    #important line so bot may process commands within the messages
    await client.process_commands(message)

#command to kick members
@client.command()
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"user {member} has been kicked!")

#error if you attempt to kick without necessary permissions
@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to kick members!")

#command to ban members
@client.command()
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"user {member} has been banned!")

#error if you attempt to ban without necessary permissions
@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to ban members!")

#command to display embed
@client.command()
async def embed(ctx):
    embed = discord.Embed(title="Car", url="https://google.com", description="I love cars!", color=0xFF5C00)
    embed.set_author(name="Ahmad S", url="https://www.linkedin.com/in/asibai7/")
    await ctx.send(embed=embed)

#command for missing permissions error
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to run this command!")

#event for private messaging a user once they leave the server
@client.event
async def on_member_remove(member):
    message = "Goodbye!"
    embed = discord.Embed(title=message)
    await member.send(embed=embed)

#event for acknowledging when a user reacts
@client.event
async def on_reaction_add(reaction, user):
    if user == client.user:
        return
    channel = reaction.message.channel
    await channel.send(f"{user.name} added: {reaction.emoji}")

#event for acknowledging when a user unreacts
@client.event
async def on_reaction_remove(reaction, user):
    if user == client.user:
        return
    channel = reaction.message.channel
    await channel.send(f"{user.name} removed: {reaction.emoji}")

#command to assign roles
@client.command()
@commands.has_permissions(manage_roles = True)
async def addRole(ctx, user : discord.Member, *, role : discord.Role):
    if role in user.roles:
        await ctx.send(f"{user.mention} already has the role, {role}")
    else:
        await user.add_roles(role)
        await ctx.send(f"Role assigned to {user.mention}")

#error if you attempt to assign role without perission
@addRole.error
async def addRole_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to use this command!")

#command to remove roles
@client.command()
@commands.has_permissions(manage_roles = True)
async def removeRole(ctx, user : discord.Member, *, role : discord.Role):
    if role in user.roles:
        await user.remove_roles(role)
        await ctx.send(f"Role: {role} removed from {user.mention}")
    else:
        await ctx.send(f"{user.mention} does not have the role, {role}")

#error if you attempt to remove role without perission
@removeRole.error
async def removeRole_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to use this command!")

#run bot with token
client.run(BotToken)