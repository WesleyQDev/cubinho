import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import random
import logging
import tomllib
from agent import llm_response

load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_version() -> str:
    """Lê a versão do pyproject.toml."""
    try:
        pyproject_path = os.path.join(os.path.dirname(__file__), "pyproject.toml")
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        return data.get("project", {}).get("version", "desconhecida")
    except Exception:
        return "desconhecida"


VERSION = get_version()


def split_message(text: str, limit: int = 1900) -> list[str]:
    """
    Divide uma mensagem longa em partes menores respeitando o limite do Discord.
    Tenta quebrar em linhas para não cortar no meio de uma frase.
    """
    if len(text) <= limit:
        return [text]
    
    parts = []
    while text:
        if len(text) <= limit:
            parts.append(text)
            break
        
        # Tenta encontrar uma quebra de linha próxima do limite
        split_index = text.rfind('\n', 0, limit)
        if split_index == -1 or split_index < limit // 2:
            # Se não encontrar, tenta espaço
            split_index = text.rfind(' ', 0, limit)
        if split_index == -1:
            # Último recurso: corta no limite
            split_index = limit
        
        parts.append(text[:split_index])
        text = text[split_index:].lstrip()
    
    return parts

intents = discord.Intents.all()
intents.message_content = True 

bot = commands.Bot(command_prefix='!', intents=intents)

# Canal onde o bot responde aleatoriamente
RANDOM_RESPONSE_CHANNEL = 1334261906717933622

# Eventos
@bot.event
async def on_ready():
    logger.info(f'O Bot está pronto. Logado como {bot.user}')
    # Sincroniza os slash commands com o Discord

    activity_watching = discord.Activity(
        type=discord.ActivityType.watching,
        name='/help'
    )

    await bot.change_presence(activity=activity_watching, status=discord.Status.online)

    try:
        synced = await bot.tree.sync()
        logger.info(f'Sincronizados {len(synced)} comandos.')
    except Exception as e:
        logger.error(f'Erro ao sincronizar comandos: {e}')

@bot.event
async def on_message(msg: discord.Message):
    # Ignora mensagens de bots (incluindo ele mesmo)
    if msg.author.bot:
        return
    
    # Responde quando alguém menciona "cubinho" na mensagem
    if "cubinho" in msg.content.lower():
        logger.info(f'Menção recebida de {msg.author}: {msg.content[:50]}...')
        async with msg.channel.typing():
            response = llm_response(msg.content, str(msg.author.id))
            if response:
                parts = split_message(response)
                for i, part in enumerate(parts):
                    if i == 0:
                        await msg.reply(part)
                    else:
                        await msg.channel.send(part)
        await bot.process_commands(msg)
        return
    
    # Resposta aleatória no canal específico (10% de chance)
    if msg.channel.id == RANDOM_RESPONSE_CHANNEL and random.random() < 0.1:
        async with msg.channel.typing():
            # Busca as últimas 10 mensagens para contexto
            messages = []
            async for message in msg.channel.history(limit=10):
                if not message.author.bot:
                    messages.append(f"{message.author.display_name}: {message.content}")
            
            # Inverte para ordem cronológica
            messages.reverse()
            
            # Monta o contexto da conversa
            context = "\n".join(messages)
            prompt = f"""Você está em um chat do Discord. Aqui está o histórico recente da conversa com os nomes dos participantes:

{context}

Responda de forma natural e descontraída à conversa, considerando o contexto e quem disse o quê. Seja breve e informal."""
            
            response = llm_response(prompt, str(msg.author.id))
            if response:
                parts = split_message(response)
                for i, part in enumerate(parts):
                    if i == 0:
                        await msg.reply(part)
                    else:
                        await msg.channel.send(part)
    
    await bot.process_commands(msg)


# Slash Commands
@bot.tree.command(name="hello", description="Diz olá!")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message('Hello world!')


@bot.tree.command(name="help", description="Mostra todos os comandos disponíveis")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🧊 Cubinho - Comandos",
        description="Sou o assistente de Engenharia de Software! Aqui estão meus comandos:",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="💬 Conversa",
        value=(
            "`/llm <texto>` - Envia uma pergunta para a IA\n"
            "`/explain <conceito> [nivel]` - Explica um conceito de forma didática\n"
            "`/search <query>` - Pesquisa informações na internet"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🔧 Utilitários",
        value=(
            "`/hello` - Diz olá!\n"
            "`/whatsapp` - Links dos grupos de WhatsApp\n"
            "`/help` - Mostra esta mensagem"
        ),
        inline=False
    )
    
    embed.add_field(
        name="💡 Dicas",
        value=(
            "• Mencione **cubinho** em qualquer mensagem para falar comigo!\n"
            "• Use `/explain` com níveis: ELI5, Iniciante, Intermediário ou Avançado\n"
            "• Use `/search` para notícias, vagas e documentação atualizada"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🌐 Open Source",
        value=(
            "Cubinho é **código aberto**! 🎉\n"
            "Contribua em: [github.com/WesleyQDev/cubinho](https://github.com/WesleyQDev/cubinho)"
        ),
        inline=False
    )
    
    embed.set_footer(text=f"v{VERSION} • Feito com 💜 para estudantes de Engenharia de Software")
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="llm", description="Envia uma pergunta para a IA")
@app_commands.describe(texto="Sua pergunta ou mensagem para a IA")
async def llm(interaction: discord.Interaction, texto: str):
    await interaction.response.defer()
    logger.info(f'Comando /llm de {interaction.user}: {texto[:50]}...')
    result = llm_response(texto, str(interaction.user.id))
    
    if not result:
        await interaction.followup.send("Sem resposta do modelo.")
        return
    
    parts = split_message(result)
    for i, part in enumerate(parts):
        if i == 0:
            await interaction.followup.send(part)
        elif interaction.channel and hasattr(interaction.channel, 'send'):
            await interaction.channel.send(part)  # type: ignore


@bot.tree.command(name="whatsapp", description="Por que usar Discord em vez de WhatsApp?")
async def whatsapp(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Grupos de whatsapp",
        description="Verique os grupos de Whatsapp no servidor da Uninter",
        color=discord.Color.purple()
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="explain", description="Explica um conceito de forma simples e didática")
@app_commands.describe(
    conceito="O conceito que você quer entender",
    nivel="Nível de explicação"
)
@app_commands.choices(nivel=[
    app_commands.Choice(name="👶 Bem simples (ELI5)", value="eli5"),
    app_commands.Choice(name="🎓 Iniciante", value="beginner"),
    app_commands.Choice(name="💻 Intermediário", value="intermediate"),
    app_commands.Choice(name="🧑‍💻 Avançado", value="advanced"),
])
async def explain(interaction: discord.Interaction, conceito: str, nivel: str = "beginner"):
    await interaction.response.defer()
    logger.info(f'Comando /explain de {interaction.user}: {conceito} ({nivel})')
    
    nivel_desc = {
        "eli5": "como se eu tivesse 5 anos, usando analogias do dia a dia",
        "beginner": "para um iniciante em programação, com exemplos simples",
        "intermediate": "para alguém que já programa, com exemplos de código",
        "advanced": "de forma técnica e aprofundada, com detalhes de implementação"
    }
    
    prompt = f"""Explique o conceito "{conceito}" {nivel_desc.get(nivel, nivel_desc['beginner'])}.

Seja claro e objetivo. Use exemplos práticos quando apropriado."""
    
    result = llm_response(prompt, str(interaction.user.id))
    
    if not result:
        await interaction.followup.send("Sem resposta do modelo.")
        return
    
    parts = split_message(result)
    for i, part in enumerate(parts):
        if i == 0:
            await interaction.followup.send(part)
        elif interaction.channel and hasattr(interaction.channel, 'send'):
            await interaction.channel.send(part)  # type: ignore


@bot.tree.command(name="search", description="Pesquisa informações atualizadas na internet")
@app_commands.describe(query="O que você quer pesquisar (notícias, vagas, documentação, etc)")
async def search(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    logger.info(f'Comando /search de {interaction.user}: {query}')
    
    prompt = f"""IMPORTANTE: Use a ferramenta de busca na web para pesquisar: "{query}"

Busque informações atualizadas e retorne os resultados mais relevantes com as fontes."""
    
    result = llm_response(prompt, str(interaction.user.id))
    
    if not result:
        await interaction.followup.send("Não encontrei resultados para essa pesquisa.")
        return
    
    parts = split_message(result)
    for i, part in enumerate(parts):
        if i == 0:
            await interaction.followup.send(part)
        elif interaction.channel and hasattr(interaction.channel, 'send'):
            await interaction.channel.send(part)  # type: ignore

    
# Run do bot
token = os.getenv('TOKEN')
if token is None:
    raise ValueError("TOKEN não encontrado nas variáveis de ambiente!")
bot.run(token)