import discord
import json
import subprocess
import sys
import os
from os.path import exists
import asyncio

if not exists('saves.json'):
    with open('saves.json', 'w') as saves:
        json.dump({'members': {}, 'lottery': {},'timer':{"daily":{},"pvp":{}},'dne':{"monsters":{}},'counting':[0,None]}, saves, indent=4)

with open('creds.json', 'r') as creds_file:
    creds = json.load(creds_file)

discordToken = creds['discordToken']

intent = discord.Intents.all()
bot = discord.Bot(intents=intent)
allCogs = ['lottery', 'econ', 'dne','counting']

@bot.event
async def on_ready():
    print("Ready\n----------------------------")

class FileManager:
    def __init__(self, bot=None):
        self.saves_file = 'saves.json'
        self.saves = None
        self.bot = bot
        self.load_saves()
        
    def load_saves(self):
        with open(self.saves_file, 'r') as saves:
            self.saves = json.load(saves)

    def save_saves(self):
        with open(self.saves_file, 'w') as saves:
            json.dump(self.saves, saves, indent=4)
        self.load_saves()

    def add_member(self, memberId):
        if memberId not in self.saves['members']:
            self.saves['members'][memberId] = [0, 0] # Holding, Bank
            self.save_saves()

    def check_member(self, memberId):
        self.load_saves()
        if self.bot:
            user = self.bot.get_user(int(memberId))
            if user is None:
                return 
        if memberId not in self.saves['members']:
            self.add_member(memberId)
            self.save_saves()

bot.file_manager = FileManager(bot)

@bot.command(description='Not for you to use')
async def reload(ctx, extension=None):
    await ctx.defer(ephemeral=True)
    if not ctx.author.guild_permissions.administrator or not await bot.is_owner(ctx.author):
        print(f"{ctx.author} tried to use the reload command")
        await ctx.respond('I told you in the description this is not for you to use, you Dingus!')
        return
    try:
        if extension is not None:
            await bot.reload_extension(f'cogs.{extension}')
        else:
            for stuff in allCogs:
                await bot.reload_extension(f'cogs.{stuff}')
        print("\n\n\n\n\n\n\n\n\n\nreloaded")
        await ctx.respond('Done', ephemeral=True)
    except discord.ExtensionError as e:
        await ctx.respond(f"Error: {str(e)}", ephemeral=True)    
    except Exception as e:
        await ctx.respond(f"Unexpected error: {str(e)}", ephemeral=True)


@bot.command(description='Not for you to use')
async def update_code(ctx, cogs:bool=False, stash:bool=False):
    if not ctx.author.guild_permissions.administrator or not await bot.is_owner(ctx.author):
        await ctx.respond('Hands off, dingus!')
        return 
    try:
        if cogs:
            for stuff in allCogs:
                subprocess.run(['git','add',f'cogs/{stuff}'])
        if stash:
            subprocess.run(['git', 'stash'])

        run = subprocess.run(["git", "pull"],capture_output=True, text=True)
        await ctx.respond(f'{run.stdout}\n\n{run.stderr}\n\nRemember to use /reload or /restart to apply the changes', ephemeral=True)
    except Exception as e:
        await ctx.respond(f"Error: {str(e)}", ephemeral=True)

@bot.command(description="This will restart the bot. Don't use unless main.py has been updated")
async def restart(ctx):
    if not ctx.author.guild_permissions.administrator or not await bot.is_owner(ctx.author):
        await ctx.respond('Hands off, dingus!')
        return
    # Check for syntax errors
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", "main.py"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        await ctx.respond(f"Syntax error detected:\n```{result.stderr}```", ephemeral=True)
        return
    await ctx.respond('Restarting bot...', ephemeral=True)
    python = sys.executable
    os.execl(python,python,*sys.argv)


@bot.command()
async def ping(ctx):
    await ctx.respond(f"Pong! Latency is {bot.latency}")
    print("recived")


for stuff in allCogs:
    bot.load_extension(f'{stuff}')   
bot.run(discordToken)




