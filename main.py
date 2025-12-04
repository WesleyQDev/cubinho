import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
load_dotenv()

intents = discord.Intents.all()
intents.message_content = True 

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'O Bot está pronto. Logado como {bot.user}')

@bot.command()
async def hello(ctx):
    await ctx.send('Hello world!')

token = os.getenv('TOKEN')
if token is None:
    raise ValueError("TOKEN não encontrado nas variáveis de ambiente!")
bot.run(token)