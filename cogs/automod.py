"""
Module AutoMod & Anti-Raid - Inspiré de : Wick, Vulcan, RaidProtect, Security Bot, AutoMod Discord, Censor Bot, MEE6 AutoMod
Fonctionnalités : anti-spam, anti-raid, anti-nuke, filtrage de mots, anti-liens, anti-mentions de masse
"""
import discord
from discord.ext import commands
from discord import app_commands
import json, os, datetime, asyncio
from collections import defaultdict

CONFIG_FILE = "data/automod_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spam_tracker = defaultdict(list)   # user_id -> [timestamps]
        self.join_tracker = defaultdict(list)    # guild_id -> [timestamps]
        self.nuke_tracker = defaultdict(list)    # guild_id -> [channel_delete_timestamps]
        self.config = load_config()

    def get_guild_config(self, guild_id):
        gid = str(guild_id)
        if gid not in self.config:
            self.config[gid] = {
                "automod_enabled": True,
                "anti_spam": True,
                "anti_raid": True,
                "anti_nuke": True,
                "anti_links": False,
                "anti_mentions": True,
                "max_mentions": 5,
                "spam_threshold": 5,
                "spam_interval": 5,
                "raid_threshold": 10,
                "raid_interval": 10,
                "nuke_threshold": 3,
                "nuke_interval": 10,
                "banned_words": [],
                "log_channel": None,
                "mute_role": None
            }
            save_config(self.config)
        return self.config[str(guild_id)]

    async def log_action(self, guild, title, description, color=discord.Color.red()):
        cfg = self.get_guild_config(guild.id)
        log_channel_id = cfg.get("log_channel")
        if log_channel_id:
            channel = guild.get_channel(int(log_channel_id))
            if channel:
                embed = discord.Embed(title=f"🛡️ AutoMod — {title}", description=description, color=color, timestamp=datetime.datetime.utcnow())
                await channel.send(embed=embed)

    # ── ANTI-SPAM ─────────────────────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        cfg = self.get_guild_config(message.guild.id)
        if not cfg.get("automod_enabled"):
            return

        uid = str(message.author.id)
        now = datetime.datetime.utcnow().timestamp()

        # Anti-spam
        if cfg.get("anti_spam"):
            self.spam_tracker[uid].append(now)
            self.spam_tracker[uid] = [t for t in self.spam_tracker[uid] if now - t < cfg["spam_interval"]]
            if len(self.spam_tracker[uid]) >= cfg["spam_threshold"]:
                try:
                    await message.author.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=5), reason="AutoMod: Spam détecté")
                    await message.channel.send(f"⚠️ {message.author.mention} a été muté pour spam.", delete_after=5)
                    await self.log_action(message.guild, "Anti-Spam", f"{message.author} muté pour spam dans {message.channel.mention}")
                    self.spam_tracker[uid] = []
                except:
                    pass

        # Anti-liens
        if cfg.get("anti_links"):
            if "http://" in message.content or "https://" in message.content or "discord.gg/" in message.content:
                if not message.author.guild_permissions.manage_messages:
                    await message.delete()
                    await message.channel.send(f"🚫 {message.author.mention} les liens ne sont pas autorisés.", delete_after=5)
                    return

        # Anti-mentions de masse
        if cfg.get("anti_mentions"):
            if len(message.mentions) >= cfg.get("max_mentions", 5):
                await message.delete()
                await message.author.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=10), reason="AutoMod: Mentions de masse")
                await message.channel.send(f"⚠️ {message.author.mention} muté pour mentions de masse.", delete_after=5)
                await self.log_action(message.guild, "Anti-Mentions", f"{message.author} muté pour {len(message.mentions)} mentions dans {message.channel.mention}")
                return

        # Filtrage de mots
        banned = cfg.get("banned_words", [])
        content_lower = message.content.lower()
        for word in banned:
            if word.lower() in content_lower:
                await message.delete()
                await message.channel.send(f"🚫 {message.author.mention} message supprimé (mot interdit).", delete_after=5)
                await self.log_action(message.guild, "Censure", f"Message de {message.author} supprimé (mot interdit: `{word}`)")
                return

    # ── ANTI-RAID ─────────────────────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member.guild:
            return
        cfg = self.get_guild_config(member.guild.id)
        if not cfg.get("anti_raid"):
            return
        gid = str(member.guild.id)
        now = datetime.datetime.utcnow().timestamp()
        self.join_tracker[gid].append(now)
        self.join_tracker[gid] = [t for t in self.join_tracker[gid] if now - t < cfg["raid_interval"]]
        if len(self.join_tracker[gid]) >= cfg["raid_threshold"]:
            # Activer la vérification
            try:
                await member.guild.edit(verification_level=discord.VerificationLevel.high)
                await self.log_action(member.guild, "🚨 Anti-Raid Activé", f"Raid détecté ! {len(self.join_tracker[gid])} membres ont rejoint en {cfg['raid_interval']}s. Niveau de vérification augmenté.", color=discord.Color.dark_red())
                self.join_tracker[gid] = []
            except:
                pass

    # ── ANTI-NUKE ─────────────────────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        guild = channel.guild
        cfg = self.get_guild_config(guild.id)
        if not cfg.get("anti_nuke"):
            return
        gid = str(guild.id)
        now = datetime.datetime.utcnow().timestamp()
        self.nuke_tracker[gid].append(now)
        self.nuke_tracker[gid] = [t for t in self.nuke_tracker[gid] if now - t < cfg["nuke_interval"]]
        if len(self.nuke_tracker[gid]) >= cfg["nuke_threshold"]:
            # Trouver le responsable via l'audit log
            try:
                async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.channel_delete):
                    if entry.user and not entry.user.bot:
                        if not entry.user.guild_permissions.administrator:
                            await entry.user.ban(reason="AutoMod Anti-Nuke: Suppression massive de salons")
                            await self.log_action(guild, "🚨 Anti-Nuke Activé", f"**{entry.user}** banni pour tentative de nuke ({len(self.nuke_tracker[gid])} salons supprimés en {cfg['nuke_interval']}s)", color=discord.Color.dark_red())
                            self.nuke_tracker[gid] = []
                            break
            except Exception as e:
                await self.log_action(guild, "Anti-Nuke Erreur", str(e))

    # ── COMMANDES DE CONFIGURATION ────────────────────────────────────────────
    @app_commands.command(name="automod", description="Configurer l'AutoMod du serveur")
    @app_commands.describe(option="Option à configurer", valeur="Valeur (true/false ou nombre)")
    @app_commands.checks.has_permissions(administrator=True)
    async def automod_cmd(self, interaction: discord.Interaction, option: str, valeur: str):
        cfg = self.get_guild_config(interaction.guild.id)
        bool_options = ["automod_enabled", "anti_spam", "anti_raid", "anti_nuke", "anti_links", "anti_mentions"]
        int_options = ["max_mentions", "spam_threshold", "spam_interval", "raid_threshold", "raid_interval", "nuke_threshold", "nuke_interval"]
        if option in bool_options:
            cfg[option] = valeur.lower() in ("true", "oui", "1", "yes")
            save_config(self.config)
            await interaction.response.send_message(f"✅ `{option}` défini à `{cfg[option]}`.")
        elif option in int_options:
            try:
                cfg[option] = int(valeur)
                save_config(self.config)
                await interaction.response.send_message(f"✅ `{option}` défini à `{valeur}`.")
            except:
                await interaction.response.send_message("❌ Valeur numérique invalide.", ephemeral=True)
        elif option == "log_channel":
            cfg["log_channel"] = valeur
            save_config(self.config)
            await interaction.response.send_message(f"✅ Salon de logs défini.")
        else:
            await interaction.response.send_message(f"❌ Option inconnue. Options : {', '.join(bool_options + int_options + ['log_channel'])}", ephemeral=True)

    @app_commands.command(name="addword", description="Ajouter un mot interdit à l'AutoMod")
    @app_commands.describe(mot="Le mot à interdire")
    @app_commands.checks.has_permissions(administrator=True)
    async def addword(self, interaction: discord.Interaction, mot: str):
        cfg = self.get_guild_config(interaction.guild.id)
        if mot.lower() not in cfg["banned_words"]:
            cfg["banned_words"].append(mot.lower())
            save_config(self.config)
        await interaction.response.send_message(f"✅ Mot `{mot}` ajouté à la liste noire.", ephemeral=True)

    @app_commands.command(name="removeword", description="Retirer un mot interdit de l'AutoMod")
    @app_commands.describe(mot="Le mot à retirer")
    @app_commands.checks.has_permissions(administrator=True)
    async def removeword(self, interaction: discord.Interaction, mot: str):
        cfg = self.get_guild_config(interaction.guild.id)
        if mot.lower() in cfg["banned_words"]:
            cfg["banned_words"].remove(mot.lower())
            save_config(self.config)
        await interaction.response.send_message(f"✅ Mot `{mot}` retiré de la liste noire.", ephemeral=True)

    @app_commands.command(name="automodstatus", description="Voir le statut de l'AutoMod")
    async def automodstatus(self, interaction: discord.Interaction):
        cfg = self.get_guild_config(interaction.guild.id)
        embed = discord.Embed(title="🛡️ Statut AutoMod", color=discord.Color.blurple())
        embed.add_field(name="AutoMod activé", value="✅" if cfg["automod_enabled"] else "❌", inline=True)
        embed.add_field(name="Anti-Spam", value="✅" if cfg["anti_spam"] else "❌", inline=True)
        embed.add_field(name="Anti-Raid", value="✅" if cfg["anti_raid"] else "❌", inline=True)
        embed.add_field(name="Anti-Nuke", value="✅" if cfg["anti_nuke"] else "❌", inline=True)
        embed.add_field(name="Anti-Liens", value="✅" if cfg["anti_links"] else "❌", inline=True)
        embed.add_field(name="Anti-Mentions", value="✅" if cfg["anti_mentions"] else "❌", inline=True)
        embed.add_field(name="Mots interdits", value=str(len(cfg["banned_words"])), inline=True)
        embed.add_field(name="Seuil spam", value=f"{cfg['spam_threshold']} msg/{cfg['spam_interval']}s", inline=True)
        embed.add_field(name="Seuil raid", value=f"{cfg['raid_threshold']} joins/{cfg['raid_interval']}s", inline=True)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
