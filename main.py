"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     BOT DISCORD ULTRA-COMPLET                              ║
║                                                                            ║
║  Regroupe les fonctionnalités de 50+ bots Discord populaires :             ║
║  MEE6, Dyno, Carl-bot, YAGPDB, Wick, Xenon, Dank Memer, OwO,              ║
║  Tickety, Giveaway Bot, FredBoat, Clyde, Security Bot, DISBOARD,           ║
║  Probot, Koya, Mimu, Arcane, Vulcan, RaidProtect, et bien d'autres...     ║
║                                                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import discord
from discord.ext import commands
import os
import asyncio
import json

# ── CONFIGURATION ─────────────────────────────────────────────────────────────
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("BOT_PREFIX", "!")

# ── INTENTS ───────────────────────────────────────────────────────────────────
intents = discord.Intents.all()  # Activer tous les intents pour une détection maximale
intents.message_content = True
intents.members = True
intents.guilds = True
intents.guild_messages = True
intents.reactions = True
intents.voice_states = True
intents.presences = True

# ── BOT ───────────────────────────────────────────────────────────────────────
bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None,
    description="Bot Discord Ultra-Complet — 50+ fonctionnalités"
)

# ── COGS (MODULES) ────────────────────────────────────────────────────────────
COGS = [
    "cogs.moderation",
    "cogs.automod",
    "cogs.tickets",
    "cogs.economy",
    "cogs.giveaway",
    "cogs.music",
    "cogs.fun",
    "cogs.ai",
    "cogs.backup",
    "cogs.setup_server",
    "cogs.special",
    "cogs.identity",
]

# Fichiers pour stocker l'identité active et les commandes actives par guilde
IDENTITY_FILE = "data/identity.json"
ACTIVE_COMMANDS_FILE = "data/active_commands.json"
BOTS_DATABASE_FILE = "data/bots_database.json"

def load_json_file(filepath: str) -> dict:
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json_file(filepath: str, data: dict):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Stockage global accessible par les cogs via bot.extras
bot.extras = {
    "bots_data": load_json_file(BOTS_DATABASE_FILE),
    "guild_identities": load_json_file(IDENTITY_FILE),
    "guild_active_commands": load_json_file(ACTIVE_COMMANDS_FILE),
    "identity_file": IDENTITY_FILE,
    "active_commands_file": ACTIVE_COMMANDS_FILE,
    "save_json_file": save_json_file
}

# Fonction pour mettre à jour les commandes actives d'une guilde
def update_guild_active_commands(guild_id: int, bot_key: str | None):
    extras = bot.extras
    if bot_key and bot_key in extras["bots_data"]:
        extras["guild_active_commands"][str(guild_id)] = extras["bots_data"][bot_key].get("active_commands", [])
    else:
        # Si pas d'identité spécifique, toutes les commandes sont actives
        # On ne peut pas lister toutes les commandes facilement ici avant le sync
        # On va mettre None pour signifier "Toutes"
        extras["guild_active_commands"].pop(str(guild_id), None)
    save_json_file(extras["active_commands_file"], extras["guild_active_commands"])

bot.extras["update_guild_active_commands"] = update_guild_active_commands

# Filtrage des commandes via on_interaction
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.application_command:
        if interaction.guild:
            guild_id_str = str(interaction.guild.id)
            active_cmds = bot.extras["guild_active_commands"].get(guild_id_str)
            
            if active_cmds is not None:
                command_name = interaction.command.name
                if command_name not in active_cmds:
                    await interaction.response.send_message(
                        f"❌ Cette commande n'est pas disponible pour l'identité actuelle du bot (**{bot.user.name}**).",
                        ephemeral=True
                    )
                    return
    
    await bot.tree.interaction_check(interaction)

async def apply_identity_on_startup(guild: discord.Guild, bot_user: discord.ClientUser):
    extras = bot.extras
    key = extras["guild_identities"].get(str(guild.id))
    if key and key in extras["bots_data"]:
        data = extras["bots_data"][key]
        try:
            if bot_user.name != data["name"]:
                await bot_user.edit(username=data["name"])
        except discord.HTTPException:
            pass
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name=data["status"]
            ),
            status=discord.Status.online
        )
        update_guild_active_commands(guild.id, key)
    else:
        update_guild_active_commands(guild.id, None)

@bot.event
async def on_ready():
    print("=" * 60)
    print(f"  Bot connecté : {bot.user.name}")
    print(f"  ID           : {bot.user.id}")
    print(f"  Serveurs     : {len(bot.guilds)}")
    print("=" * 60)

    for guild in bot.guilds:
        await apply_identity_on_startup(guild, bot.user)

    try:
        synced = await bot.tree.sync()
        print(f"  Slash commands synchronisées : {len(synced)}")
    except Exception as e:
        print(f"  Erreur sync : {e}")
    print("=" * 60)
    print("  ✅ Bot prêt !")
    print("=" * 60)

async def load_cogs():
    os.makedirs("data", exist_ok=True)
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            print(f"  ✅ Module chargé : {cog}")
        except Exception as e:
            print(f"  ❌ Erreur module {cog} : {e}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
