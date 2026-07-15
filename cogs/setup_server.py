"""
Module Setup Serveur - Inspiré de : SCNX, Dyno Custom Bot, MEE6 Private Bot, Probot
Fonctionnalités : setup complet d'un serveur Discord (salons, rôles, catégories, welcome, logs)
Supprime les anciens salons et crée une structure propre et professionnelle
"""
import discord
from discord.ext import commands
from discord import app_commands
import asyncio, json, os

SETUP_CONFIG_FILE = "data/setup_config.json"

def load_setup_config():
    if os.path.exists(SETUP_CONFIG_FILE):
        with open(SETUP_CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_setup_config(data):
    with open(SETUP_CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Structure de serveur par défaut
DEFAULT_STRUCTURE = {
    "categories": [
        {
            "name": "📢 INFORMATIONS",
            "channels": [
                {"name": "📜│règles", "type": "text", "topic": "Règles du serveur"},
                {"name": "📣│annonces", "type": "text", "topic": "Annonces officielles"},
                {"name": "🗓️│événements", "type": "text", "topic": "Événements du serveur"},
                {"name": "📊│statistiques", "type": "text", "topic": "Statistiques du serveur"},
            ]
        },
        {
            "name": "👋 ACCUEIL",
            "channels": [
                {"name": "🎉│bienvenue", "type": "text", "topic": "Bienvenue sur le serveur !"},
                {"name": "👋│présentations", "type": "text", "topic": "Présentez-vous ici"},
                {"name": "🎭│rôles", "type": "text", "topic": "Choisissez vos rôles"},
            ]
        },
        {
            "name": "💬 GÉNÉRAL",
            "channels": [
                {"name": "💬│général", "type": "text", "topic": "Discussion générale"},
                {"name": "🖼️│médias", "type": "text", "topic": "Partagez vos médias"},
                {"name": "😂│memes", "type": "text", "topic": "Partagez vos mèmes"},
                {"name": "🤖│commandes-bot", "type": "text", "topic": "Utilisez les commandes du bot ici"},
            ]
        },
        {
            "name": "🎮 JEUX",
            "channels": [
                {"name": "🎮│gaming", "type": "text", "topic": "Discussion gaming"},
                {"name": "🏆│classements", "type": "text", "topic": "Classements et scores"},
            ]
        },
        {
            "name": "🎵 MUSIQUE",
            "channels": [
                {"name": "🎵│musique", "type": "text", "topic": "Commandes musicales"},
                {"name": "🎤│vocal-général", "type": "voice"},
                {"name": "🎮│vocal-gaming", "type": "voice"},
                {"name": "🎵│vocal-musique", "type": "voice"},
            ]
        },
        {
            "name": "🛡️ MODÉRATION",
            "channels": [
                {"name": "📋│logs-modération", "type": "text", "topic": "Logs de modération"},
                {"name": "🚨│logs-automod", "type": "text", "topic": "Logs AutoMod"},
                {"name": "📊│logs-membres", "type": "text", "topic": "Arrivées et départs"},
                {"name": "🔒│staff-chat", "type": "text", "topic": "Chat privé du staff"},
            ]
        },
        {
            "name": "🎫 SUPPORT",
            "channels": [
                {"name": "📩│ouvrir-ticket", "type": "text", "topic": "Ouvrez un ticket de support"},
            ]
        },
    ],
    "roles": [
        {"name": "👑 Propriétaire", "color": 0xFFD700, "hoist": True, "permissions": 8},
        {"name": "⚙️ Administrateur", "color": 0xFF4500, "hoist": True, "permissions": 8},
        {"name": "🛡️ Modérateur", "color": 0x00BFFF, "hoist": True, "permissions": 0x4000000},
        {"name": "🌟 VIP", "color": 0x9B59B6, "hoist": True, "permissions": 0x400000},
        {"name": "✅ Vérifié", "color": 0x2ECC71, "hoist": False, "permissions": 0x400000},
        {"name": "🤖 Bot", "color": 0x95A5A6, "hoist": True, "permissions": 0x8},
        {"name": "👤 Membre", "color": 0x3498DB, "hoist": False, "permissions": 0x400000},
    ]
}

class SetupServer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup", description="Setup complet du serveur (supprime et recrée les salons)")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction):
        # Confirmation
        embed = discord.Embed(
            title="⚠️ ATTENTION — Setup Serveur",
            description="Cette commande va **supprimer TOUS les salons et catégories existants** et créer une nouvelle structure propre.\n\n**Cette action est irréversible !**\n\nConfirmez en cliquant sur le bouton ci-dessous.",
            color=discord.Color.red()
        )
        view = SetupConfirmView(interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="setwelcome", description="Configurer le message de bienvenue")
    @app_commands.describe(salon="Le salon de bienvenue", message="Le message (utilisez {user} et {server}")
    @app_commands.checks.has_permissions(administrator=True)
    async def setwelcome(self, interaction: discord.Interaction, salon: discord.TextChannel, message: str = None):
        config = load_setup_config()
        gid = str(interaction.guild.id)
        if gid not in config:
            config[gid] = {}
        config[gid]["welcome_channel"] = str(salon.id)
        config[gid]["welcome_message"] = message or "Bienvenue {user} sur **{server}** ! 🎉"
        save_setup_config(config)
        await interaction.response.send_message(f"✅ Message de bienvenue configuré dans {salon.mention}.")

    @app_commands.command(name="setlogs", description="Configurer le salon de logs")
    @app_commands.describe(salon="Le salon de logs")
    @app_commands.checks.has_permissions(administrator=True)
    async def setlogs(self, interaction: discord.Interaction, salon: discord.TextChannel):
        config = load_setup_config()
        gid = str(interaction.guild.id)
        if gid not in config:
            config[gid] = {}
        config[gid]["log_channel"] = str(salon.id)
        save_setup_config(config)
        await interaction.response.send_message(f"✅ Salon de logs configuré : {salon.mention}.")

    @app_commands.command(name="setverify", description="Configurer le rôle de vérification")
    @app_commands.describe(role="Le rôle à donner après vérification")
    @app_commands.checks.has_permissions(administrator=True)
    async def setverify(self, interaction: discord.Interaction, role: discord.Role):
        config = load_setup_config()
        gid = str(interaction.guild.id)
        if gid not in config:
            config[gid] = {}
        config[gid]["verify_role"] = str(role.id)
        save_setup_config(config)
        await interaction.response.send_message(f"✅ Rôle de vérification : {role.mention}.")

    @app_commands.command(name="verify", description="Se vérifier sur le serveur")
    async def verify(self, interaction: discord.Interaction):
        config = load_setup_config()
        gid = str(interaction.guild.id)
        cfg = config.get(gid, {})
        role_id = cfg.get("verify_role")
        if not role_id:
            await interaction.response.send_message("❌ Aucun rôle de vérification configuré.", ephemeral=True)
            return
        role = interaction.guild.get_role(int(role_id))
        if not role:
            await interaction.response.send_message("❌ Rôle introuvable.", ephemeral=True)
            return
        if role in interaction.user.roles:
            await interaction.response.send_message("✅ Tu es déjà vérifié !", ephemeral=True)
            return
        await interaction.user.add_roles(role)
        await interaction.response.send_message(f"✅ Tu es maintenant vérifié ! Rôle {role.mention} attribué.", ephemeral=True)

    # ── EVENTS ────────────────────────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_member_join(self, member):
        config = load_setup_config()
        gid = str(member.guild.id)
        cfg = config.get(gid, {})
        welcome_channel_id = cfg.get("welcome_channel")
        if welcome_channel_id:
            channel = member.guild.get_channel(int(welcome_channel_id))
            if channel:
                msg = cfg.get("welcome_message", "Bienvenue {user} sur **{server}** ! 🎉")
                msg = msg.replace("{user}", member.mention).replace("{server}", member.guild.name)
                embed = discord.Embed(
                    title="👋 Nouveau Membre !",
                    description=msg,
                    color=discord.Color.green()
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.add_field(name="Membre", value=member.mention, inline=True)
                embed.add_field(name="Membres total", value=str(member.guild.member_count), inline=True)
                await channel.send(embed=embed)
        log_channel_id = cfg.get("log_channel")
        if log_channel_id:
            channel = member.guild.get_channel(int(log_channel_id))
            if channel:
                embed = discord.Embed(title="📥 Membre Rejoint", color=discord.Color.green())
                embed.add_field(name="Membre", value=f"{member} ({member.id})", inline=False)
                embed.add_field(name="Compte créé", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        config = load_setup_config()
        gid = str(member.guild.id)
        cfg = config.get(gid, {})
        log_channel_id = cfg.get("log_channel")
        if log_channel_id:
            channel = member.guild.get_channel(int(log_channel_id))
            if channel:
                embed = discord.Embed(title="📤 Membre Parti", color=discord.Color.red())
                embed.add_field(name="Membre", value=f"{member} ({member.id})", inline=False)
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        config = load_setup_config()
        gid = str(message.guild.id) if message.guild else None
        if not gid:
            return
        cfg = config.get(gid, {})
        log_channel_id = cfg.get("log_channel")
        if log_channel_id:
            channel = message.guild.get_channel(int(log_channel_id))
            if channel and channel.id != message.channel.id:
                embed = discord.Embed(title="🗑️ Message Supprimé", color=discord.Color.orange())
                embed.add_field(name="Auteur", value=message.author.mention, inline=True)
                embed.add_field(name="Salon", value=message.channel.mention, inline=True)
                embed.add_field(name="Contenu", value=message.content[:1024] if message.content else "*(vide)*", inline=False)
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return
        config = load_setup_config()
        gid = str(before.guild.id) if before.guild else None
        if not gid:
            return
        cfg = config.get(gid, {})
        log_channel_id = cfg.get("log_channel")
        if log_channel_id:
            channel = before.guild.get_channel(int(log_channel_id))
            if channel:
                embed = discord.Embed(title="✏️ Message Modifié", color=discord.Color.yellow())
                embed.add_field(name="Auteur", value=before.author.mention, inline=True)
                embed.add_field(name="Salon", value=before.channel.mention, inline=True)
                embed.add_field(name="Avant", value=before.content[:512] if before.content else "*(vide)*", inline=False)
                embed.add_field(name="Après", value=after.content[:512] if after.content else "*(vide)*", inline=False)
                await channel.send(embed=embed)


class SetupConfirmView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=60)
        self.user_id = user_id

    @discord.ui.button(label="✅ Confirmer le Setup", style=discord.ButtonStyle.danger, custom_id="confirm_setup")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seul l'administrateur peut confirmer.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        await interaction.followup.send("⏳ Setup en cours... Cela peut prendre quelques minutes.", ephemeral=True)

        # Supprimer tous les salons existants
        for channel in guild.channels:
            try:
                await channel.delete()
                await asyncio.sleep(0.3)
            except:
                pass

        # Créer les rôles
        created_roles = {}
        for role_data in DEFAULT_STRUCTURE["roles"]:
            try:
                role = await guild.create_role(
                    name=role_data["name"],
                    color=discord.Color(role_data["color"]),
                    hoist=role_data["hoist"],
                    permissions=discord.Permissions(role_data["permissions"])
                )
                created_roles[role_data["name"]] = role
                await asyncio.sleep(0.3)
            except:
                pass

        # Créer les catégories et salons
        for cat_data in DEFAULT_STRUCTURE["categories"]:
            try:
                # Permissions spéciales pour la catégorie modération
                overwrites = {}
                if "MODÉRATION" in cat_data["name"].upper():
                    overwrites = {
                        guild.default_role: discord.PermissionOverwrite(read_messages=False)
                    }
                    mod_role = created_roles.get("🛡️ Modérateur")
                    if mod_role:
                        overwrites[mod_role] = discord.PermissionOverwrite(read_messages=True)
                cat = await guild.create_category(cat_data["name"], overwrites=overwrites)
                await asyncio.sleep(0.3)
                for ch_data in cat_data.get("channels", []):
                    try:
                        if ch_data["type"] == "text":
                            await guild.create_text_channel(
                                ch_data["name"],
                                category=cat,
                                topic=ch_data.get("topic", "")
                            )
                        elif ch_data["type"] == "voice":
                            await guild.create_voice_channel(ch_data["name"], category=cat)
                        await asyncio.sleep(0.3)
                    except:
                        pass
            except:
                pass

        # Message de confirmation dans le premier salon texte disponible
        for channel in guild.text_channels:
            try:
                embed = discord.Embed(
                    title="✅ Setup Serveur Terminé !",
                    description="Le serveur a été configuré avec succès.\n\nUtilisez `/setwelcome`, `/setlogs` et `/setverify` pour finaliser la configuration.",
                    color=discord.Color.green()
                )
                embed.add_field(name="Catégories créées", value=str(len(DEFAULT_STRUCTURE["categories"])), inline=True)
                embed.add_field(name="Rôles créés", value=str(len(DEFAULT_STRUCTURE["roles"])), inline=True)
                await channel.send(embed=embed)
                break
            except:
                pass

    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.secondary, custom_id="cancel_setup")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ Setup annulé.", ephemeral=True)
        self.stop()

async def setup(bot):
    await bot.add_cog(SetupServer(bot))
