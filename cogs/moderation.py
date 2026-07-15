"""
Module Modération - Inspiré de : MEE6, Dyno, Carl-bot, Probot, YAGPDB, Wick, Vulcan, RaidProtect
Commandes : ban, kick, mute, warn, clear, slowmode, lock, unlock, role, nickname, timeout
"""
import discord
from discord.ext import commands
from discord import app_commands
import json, os, datetime

WARNS_FILE = "data/warns.json"

def load_warns():
    if os.path.exists(WARNS_FILE):
        with open(WARNS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_warns(data):
    with open(WARNS_FILE, "w") as f:
        json.dump(data, f, indent=2)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── BAN ──────────────────────────────────────────────────────────────────
    @app_commands.command(name="ban", description="Bannir un membre du serveur")
    @app_commands.describe(membre="Le membre à bannir", raison="Raison du bannissement")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, membre: discord.Member, raison: str = "Aucune raison fournie"):
        await membre.ban(reason=raison)
        embed = discord.Embed(title="🔨 Membre Banni", color=discord.Color.red())
        embed.add_field(name="Membre", value=f"{membre.mention}", inline=True)
        embed.add_field(name="Modérateur", value=interaction.user.mention, inline=True)
        embed.add_field(name="Raison", value=raison, inline=False)
        embed.set_footer(text=f"ID: {membre.id}")
        await interaction.response.send_message(embed=embed)

    # ── UNBAN ─────────────────────────────────────────────────────────────────
    @app_commands.command(name="unban", description="Débannir un utilisateur")
    @app_commands.describe(user_id="L'ID de l'utilisateur à débannir")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str):
        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user)
            embed = discord.Embed(title="✅ Membre Débanni", color=discord.Color.green())
            embed.add_field(name="Utilisateur", value=f"{user}", inline=True)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur : {e}", ephemeral=True)

    # ── KICK ──────────────────────────────────────────────────────────────────
    @app_commands.command(name="kick", description="Expulser un membre du serveur")
    @app_commands.describe(membre="Le membre à expulser", raison="Raison de l'expulsion")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, membre: discord.Member, raison: str = "Aucune raison fournie"):
        await membre.kick(reason=raison)
        embed = discord.Embed(title="👢 Membre Expulsé", color=discord.Color.orange())
        embed.add_field(name="Membre", value=membre.mention, inline=True)
        embed.add_field(name="Modérateur", value=interaction.user.mention, inline=True)
        embed.add_field(name="Raison", value=raison, inline=False)
        await interaction.response.send_message(embed=embed)

    # ── MUTE (TIMEOUT) ────────────────────────────────────────────────────────
    @app_commands.command(name="mute", description="Mettre en sourdine un membre (timeout)")
    @app_commands.describe(membre="Le membre à muter", duree="Durée en minutes", raison="Raison")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, membre: discord.Member, duree: int = 10, raison: str = "Aucune raison fournie"):
        until = discord.utils.utcnow() + datetime.timedelta(minutes=duree)
        await membre.timeout(until, reason=raison)
        embed = discord.Embed(title="🔇 Membre Muté", color=discord.Color.yellow())
        embed.add_field(name="Membre", value=membre.mention, inline=True)
        embed.add_field(name="Durée", value=f"{duree} minutes", inline=True)
        embed.add_field(name="Raison", value=raison, inline=False)
        await interaction.response.send_message(embed=embed)

    # ── UNMUTE ────────────────────────────────────────────────────────────────
    @app_commands.command(name="unmute", description="Retirer le timeout d'un membre")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, membre: discord.Member):
        await membre.timeout(None)
        embed = discord.Embed(title="🔊 Membre Démuté", color=discord.Color.green())
        embed.add_field(name="Membre", value=membre.mention, inline=True)
        await interaction.response.send_message(embed=embed)

    # ── WARN ──────────────────────────────────────────────────────────────────
    @app_commands.command(name="warn", description="Avertir un membre")
    @app_commands.describe(membre="Le membre à avertir", raison="Raison de l'avertissement")
    @app_commands.checks.has_permissions(kick_members=True)
    async def warn(self, interaction: discord.Interaction, membre: discord.Member, raison: str = "Aucune raison fournie"):
        warns = load_warns()
        guild_id = str(interaction.guild.id)
        user_id = str(membre.id)
        if guild_id not in warns:
            warns[guild_id] = {}
        if user_id not in warns[guild_id]:
            warns[guild_id][user_id] = []
        warns[guild_id][user_id].append({
            "raison": raison,
            "moderateur": str(interaction.user),
            "date": str(datetime.datetime.utcnow())
        })
        save_warns(warns)
        count = len(warns[guild_id][user_id])
        embed = discord.Embed(title="⚠️ Avertissement", color=discord.Color.yellow())
        embed.add_field(name="Membre", value=membre.mention, inline=True)
        embed.add_field(name="Avertissements", value=f"{count}", inline=True)
        embed.add_field(name="Raison", value=raison, inline=False)
        await interaction.response.send_message(embed=embed)
        try:
            await membre.send(f"⚠️ Tu as reçu un avertissement sur **{interaction.guild.name}** : {raison}")
        except:
            pass

    # ── WARNINGS ──────────────────────────────────────────────────────────────
    @app_commands.command(name="warnings", description="Voir les avertissements d'un membre")
    @app_commands.describe(membre="Le membre à vérifier")
    async def warnings(self, interaction: discord.Interaction, membre: discord.Member):
        warns = load_warns()
        guild_id = str(interaction.guild.id)
        user_id = str(membre.id)
        user_warns = warns.get(guild_id, {}).get(user_id, [])
        embed = discord.Embed(title=f"⚠️ Avertissements de {membre.display_name}", color=discord.Color.yellow())
        if not user_warns:
            embed.description = "Aucun avertissement."
        else:
            for i, w in enumerate(user_warns, 1):
                embed.add_field(name=f"#{i} — {w['date'][:10]}", value=f"**Raison :** {w['raison']}\n**Modérateur :** {w['moderateur']}", inline=False)
        await interaction.response.send_message(embed=embed)

    # ── CLEARWARNS ────────────────────────────────────────────────────────────
    @app_commands.command(name="clearwarns", description="Effacer les avertissements d'un membre")
    @app_commands.checks.has_permissions(administrator=True)
    async def clearwarns(self, interaction: discord.Interaction, membre: discord.Member):
        warns = load_warns()
        guild_id = str(interaction.guild.id)
        user_id = str(membre.id)
        if guild_id in warns and user_id in warns[guild_id]:
            warns[guild_id][user_id] = []
            save_warns(warns)
        await interaction.response.send_message(f"✅ Avertissements de {membre.mention} effacés.", ephemeral=True)

    # ── CLEAR / PURGE ─────────────────────────────────────────────────────────
    @app_commands.command(name="clear", description="Supprimer des messages en masse")
    @app_commands.describe(nombre="Nombre de messages à supprimer (max 100)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, nombre: int = 10):
        if nombre > 100:
            nombre = 100
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=nombre)
        await interaction.followup.send(f"🗑️ {len(deleted)} messages supprimés.", ephemeral=True)

    # ── SLOWMODE ──────────────────────────────────────────────────────────────
    @app_commands.command(name="slowmode", description="Définir le mode lent d'un salon")
    @app_commands.describe(secondes="Délai en secondes (0 pour désactiver)")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, secondes: int = 0):
        await interaction.channel.edit(slowmode_delay=secondes)
        if secondes == 0:
            await interaction.response.send_message("✅ Mode lent désactivé.")
        else:
            await interaction.response.send_message(f"✅ Mode lent défini à **{secondes}s**.")

    # ── LOCK ──────────────────────────────────────────────────────────────────
    @app_commands.command(name="lock", description="Verrouiller un salon")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lock(self, interaction: discord.Interaction):
        overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = False
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message("🔒 Salon verrouillé.")

    # ── UNLOCK ────────────────────────────────────────────────────────────────
    @app_commands.command(name="unlock", description="Déverrouiller un salon")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction):
        overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = True
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message("🔓 Salon déverrouillé.")

    # ── NICK ──────────────────────────────────────────────────────────────────
    @app_commands.command(name="nick", description="Changer le surnom d'un membre")
    @app_commands.describe(membre="Le membre", surnom="Nouveau surnom (vide = réinitialiser)")
    @app_commands.checks.has_permissions(manage_nicknames=True)
    async def nick(self, interaction: discord.Interaction, membre: discord.Member, surnom: str = None):
        await membre.edit(nick=surnom)
        if surnom:
            await interaction.response.send_message(f"✅ Surnom de {membre.mention} changé en **{surnom}**.")
        else:
            await interaction.response.send_message(f"✅ Surnom de {membre.mention} réinitialisé.")

    # ── ROLE ADD/REMOVE ───────────────────────────────────────────────────────
    @app_commands.command(name="role", description="Ajouter ou retirer un rôle à un membre")
    @app_commands.describe(membre="Le membre", role="Le rôle", action="add ou remove")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def role(self, interaction: discord.Interaction, membre: discord.Member, role: discord.Role, action: str = "add"):
        if action == "add":
            await membre.add_roles(role)
            await interaction.response.send_message(f"✅ Rôle {role.mention} ajouté à {membre.mention}.")
        elif action == "remove":
            await membre.remove_roles(role)
            await interaction.response.send_message(f"✅ Rôle {role.mention} retiré de {membre.mention}.")
        else:
            await interaction.response.send_message("❌ Action invalide. Utilise `add` ou `remove`.", ephemeral=True)

    # ── USERINFO ──────────────────────────────────────────────────────────────
    @app_commands.command(name="userinfo", description="Afficher les informations d'un membre")
    @app_commands.describe(membre="Le membre à inspecter")
    async def userinfo(self, interaction: discord.Interaction, membre: discord.Member = None):
        membre = membre or interaction.user
        embed = discord.Embed(title=f"👤 Informations — {membre}", color=membre.color)
        embed.set_thumbnail(url=membre.display_avatar.url)
        embed.add_field(name="ID", value=membre.id, inline=True)
        embed.add_field(name="Surnom", value=membre.display_name, inline=True)
        embed.add_field(name="Compte créé", value=membre.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="A rejoint", value=membre.joined_at.strftime("%d/%m/%Y") if membre.joined_at else "Inconnu", inline=True)
        roles = [r.mention for r in membre.roles if r.name != "@everyone"]
        embed.add_field(name=f"Rôles ({len(roles)})", value=" ".join(roles) if roles else "Aucun", inline=False)
        await interaction.response.send_message(embed=embed)

    # ── SERVERINFO ────────────────────────────────────────────────────────────
    @app_commands.command(name="serverinfo", description="Afficher les informations du serveur")
    async def serverinfo(self, interaction: discord.Interaction):
        g = interaction.guild
        embed = discord.Embed(title=f"🏠 {g.name}", color=discord.Color.blurple())
        if g.icon:
            embed.set_thumbnail(url=g.icon.url)
        embed.add_field(name="ID", value=g.id, inline=True)
        embed.add_field(name="Propriétaire", value=g.owner.mention if g.owner else "Inconnu", inline=True)
        embed.add_field(name="Membres", value=g.member_count, inline=True)
        embed.add_field(name="Salons", value=len(g.channels), inline=True)
        embed.add_field(name="Rôles", value=len(g.roles), inline=True)
        embed.add_field(name="Créé le", value=g.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Niveau de boost", value=g.premium_tier, inline=True)
        embed.add_field(name="Boosts", value=g.premium_subscription_count, inline=True)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
