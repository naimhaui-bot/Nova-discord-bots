"""
Module Fun & Jeux - Inspiré de : Dark Memer, OwO, Dank Memer, Grow a Tree, Make it a Quote, Counting Bot, Conquest, NebulaBot
Fonctionnalités : 8ball, meme, quote, hug, pat, slap, coinflip, rps, counting, owo, tree
"""
import discord
from discord.ext import commands
from discord import app_commands
import random, json, os, datetime, asyncio

TREE_FILE = "data/trees.json"
COUNTING_FILE = "data/counting.json"

def load_trees():
    if os.path.exists(TREE_FILE):
        with open(TREE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_trees(data):
    with open(TREE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_counting():
    if os.path.exists(COUNTING_FILE):
        with open(COUNTING_FILE, "r") as f:
            return json.load(f)
    return {}

def save_counting(data):
    with open(COUNTING_FILE, "w") as f:
        json.dump(data, f, indent=2)

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── 8BALL ─────────────────────────────────────────────────────────────────
    @app_commands.command(name="8ball", description="Poser une question à la boule magique")
    @app_commands.describe(question="Ta question")
    async def eightball(self, interaction: discord.Interaction, question: str):
        responses = [
            "🟢 Oui, absolument !", "🟢 C'est certain.", "🟢 Sans aucun doute.",
            "🟢 Oui, définitivement.", "🟢 Tu peux compter dessus.",
            "🟡 Peut-être...", "🟡 Difficile à dire.", "🟡 Concentre-toi et redemande.",
            "🔴 Non, je ne pense pas.", "🔴 Absolument pas.", "🔴 Mes sources disent non.",
            "🔴 Très douteux.", "🔴 Oublie ça."
        ]
        embed = discord.Embed(title="🎱 Boule Magique", color=discord.Color.purple())
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Réponse", value=random.choice(responses), inline=False)
        await interaction.response.send_message(embed=embed)

    # ── COINFLIP ──────────────────────────────────────────────────────────────
    @app_commands.command(name="coinflip", description="Lancer une pièce")
    async def coinflip(self, interaction: discord.Interaction):
        result = random.choice(["🪙 Pile !", "🪙 Face !"])
        await interaction.response.send_message(result)

    # ── RPS ───────────────────────────────────────────────────────────────────
    @app_commands.command(name="rps", description="Pierre, Feuille, Ciseaux")
    @app_commands.describe(choix="pierre, feuille ou ciseaux")
    async def rps(self, interaction: discord.Interaction, choix: str):
        choices = ["pierre", "feuille", "ciseaux"]
        emojis = {"pierre": "🪨", "feuille": "📄", "ciseaux": "✂️"}
        choix = choix.lower()
        if choix not in choices:
            await interaction.response.send_message("❌ Choix invalide. Utilise `pierre`, `feuille` ou `ciseaux`.", ephemeral=True)
            return
        bot_choice = random.choice(choices)
        wins = {"pierre": "ciseaux", "feuille": "pierre", "ciseaux": "feuille"}
        if choix == bot_choice:
            result = "🤝 Égalité !"
        elif wins[choix] == bot_choice:
            result = "🎉 Tu as gagné !"
        else:
            result = "😢 Tu as perdu !"
        embed = discord.Embed(title="🎮 Pierre, Feuille, Ciseaux", color=discord.Color.blurple())
        embed.add_field(name="Ton choix", value=f"{emojis[choix]} {choix.capitalize()}", inline=True)
        embed.add_field(name="Mon choix", value=f"{emojis[bot_choice]} {bot_choice.capitalize()}", inline=True)
        embed.add_field(name="Résultat", value=result, inline=False)
        await interaction.response.send_message(embed=embed)

    # ── HUG / PAT / SLAP ──────────────────────────────────────────────────────
    @app_commands.command(name="hug", description="Faire un câlin à quelqu'un")
    @app_commands.describe(membre="La personne à câliner")
    async def hug(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.response.send_message(f"🤗 {interaction.user.mention} fait un câlin à {membre.mention} !")

    @app_commands.command(name="pat", description="Tapoter la tête de quelqu'un")
    @app_commands.describe(membre="La personne à tapoter")
    async def pat(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.response.send_message(f"👋 {interaction.user.mention} tapote la tête de {membre.mention} !")

    @app_commands.command(name="slap", description="Gifler quelqu'un")
    @app_commands.describe(membre="La personne à gifler")
    async def slap(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.response.send_message(f"👋 {interaction.user.mention} gifle {membre.mention} !")

    # ── QUOTE ─────────────────────────────────────────────────────────────────
    @app_commands.command(name="quote", description="Créer une citation stylée (Make it a Quote)")
    @app_commands.describe(texte="Le texte à citer", auteur="L'auteur de la citation")
    async def quote(self, interaction: discord.Interaction, texte: str, auteur: str = None):
        auteur = auteur or interaction.user.display_name
        embed = discord.Embed(
            description=f"*« {texte} »*",
            color=discord.Color.dark_gray()
        )
        embed.set_footer(text=f"— {auteur}")
        await interaction.response.send_message(embed=embed)

    # ── OWO ───────────────────────────────────────────────────────────────────
    @app_commands.command(name="owo", description="Transformer du texte en OwO")
    @app_commands.describe(texte="Le texte à transformer")
    async def owo(self, interaction: discord.Interaction, texte: str):
        result = texte.replace("r", "w").replace("l", "w").replace("R", "W").replace("L", "W")
        result = result.replace("n", "ny").replace("N", "Ny")
        faces = ["OwO", "UwU", ">w<", "^w^", "~w~"]
        result += f" {random.choice(faces)}"
        await interaction.response.send_message(result)

    # ── GROW A TREE ───────────────────────────────────────────────────────────
    @app_commands.command(name="water", description="Arroser votre arbre (Grow a Tree)")
    async def water(self, interaction: discord.Interaction):
        trees = load_trees()
        gid, uid = str(interaction.guild.id), str(interaction.user.id)
        if gid not in trees:
            trees[gid] = {}
        if uid not in trees[gid]:
            trees[gid][uid] = {"size": 0, "last_water": None, "name": "Mon Arbre"}
        tree = trees[gid][uid]
        now = datetime.datetime.utcnow()
        last = tree.get("last_water")
        if last:
            last_dt = datetime.datetime.fromisoformat(last)
            diff = (now - last_dt).total_seconds()
            if diff < 3600:
                remaining = int((3600 - diff) / 60)
                await interaction.response.send_message(f"🌳 Ton arbre a déjà été arrosé ! Reviens dans **{remaining} minutes**.", ephemeral=True)
                return
        growth = random.randint(1, 5)
        tree["size"] += growth
        tree["last_water"] = now.isoformat()
        save_trees(trees)
        size = tree["size"]
        if size < 10:
            emoji = "🌱"
        elif size < 30:
            emoji = "🌿"
        elif size < 60:
            emoji = "🌲"
        else:
            emoji = "🌳"
        embed = discord.Embed(title=f"{emoji} Arbre de {interaction.user.display_name}", color=discord.Color.green())
        embed.add_field(name="Taille", value=f"{size} cm (+{growth})", inline=True)
        embed.add_field(name="Stade", value=emoji, inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tree", description="Voir votre arbre ou celui d'un membre")
    @app_commands.describe(membre="Le membre (optionnel)")
    async def tree(self, interaction: discord.Interaction, membre: discord.Member = None):
        membre = membre or interaction.user
        trees = load_trees()
        gid, uid = str(interaction.guild.id), str(membre.id)
        tree = trees.get(gid, {}).get(uid, {"size": 0})
        size = tree["size"]
        if size < 10:
            emoji, stage = "🌱", "Graine"
        elif size < 30:
            emoji, stage = "🌿", "Pousse"
        elif size < 60:
            emoji, stage = "🌲", "Arbre"
        else:
            emoji, stage = "🌳", "Grand Arbre"
        embed = discord.Embed(title=f"{emoji} Arbre de {membre.display_name}", color=discord.Color.green())
        embed.add_field(name="Taille", value=f"{size} cm", inline=True)
        embed.add_field(name="Stade", value=stage, inline=True)
        await interaction.response.send_message(embed=embed)

    # ── COUNTING BOT ──────────────────────────────────────────────────────────
    @app_commands.command(name="setcounting", description="Définir le salon de comptage")
    @app_commands.checks.has_permissions(administrator=True)
    async def setcounting(self, interaction: discord.Interaction):
        counting = load_counting()
        gid = str(interaction.guild.id)
        counting[gid] = {"channel_id": str(interaction.channel.id), "count": 0, "last_user": None}
        save_counting(counting)
        await interaction.response.send_message(f"✅ Salon de comptage défini sur {interaction.channel.mention}. Commencez à compter depuis **1** !")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        counting = load_counting()
        gid = str(message.guild.id)
        if gid not in counting:
            return
        data = counting[gid]
        if str(message.channel.id) != data.get("channel_id"):
            return
        try:
            number = int(message.content.strip())
        except:
            await message.delete()
            await message.channel.send(f"❌ {message.author.mention} a cassé le comptage ! Recommencez depuis **1**.", delete_after=5)
            counting[gid]["count"] = 0
            counting[gid]["last_user"] = None
            save_counting(counting)
            return
        expected = data["count"] + 1
        if number != expected:
            await message.delete()
            await message.channel.send(f"❌ {message.author.mention} a cassé le comptage ! Recommencez depuis **1**.", delete_after=5)
            counting[gid]["count"] = 0
            counting[gid]["last_user"] = None
            save_counting(counting)
            return
        if str(message.author.id) == data.get("last_user"):
            await message.delete()
            await message.channel.send(f"❌ {message.author.mention} tu ne peux pas compter deux fois de suite !", delete_after=5)
            return
        counting[gid]["count"] = number
        counting[gid]["last_user"] = str(message.author.id)
        save_counting(counting)
        await message.add_reaction("✅")

    # ── DICE ──────────────────────────────────────────────────────────────────
    @app_commands.command(name="dice", description="Lancer un dé")
    @app_commands.describe(faces="Nombre de faces (défaut: 6)")
    async def dice(self, interaction: discord.Interaction, faces: int = 6):
        result = random.randint(1, faces)
        await interaction.response.send_message(f"🎲 Tu as lancé un dé à **{faces}** faces et obtenu : **{result}** !")

    # ── POLL ──────────────────────────────────────────────────────────────────
    @app_commands.command(name="poll", description="Créer un sondage")
    @app_commands.describe(question="La question du sondage")
    async def poll(self, interaction: discord.Interaction, question: str):
        embed = discord.Embed(title="📊 Sondage", description=question, color=discord.Color.blurple())
        embed.set_footer(text=f"Sondage par {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")
        await msg.add_reaction("🤷")

    # ── AVATAR ────────────────────────────────────────────────────────────────
    @app_commands.command(name="avatar", description="Voir l'avatar d'un membre")
    @app_commands.describe(membre="Le membre (optionnel)")
    async def avatar(self, interaction: discord.Interaction, membre: discord.Member = None):
        membre = membre or interaction.user
        embed = discord.Embed(title=f"🖼️ Avatar de {membre.display_name}", color=discord.Color.blurple())
        embed.set_image(url=membre.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    # ── INVITE MANAGER ────────────────────────────────────────────────────────
    @app_commands.command(name="invites", description="Voir les invitations d'un membre")
    @app_commands.describe(membre="Le membre (optionnel)")
    async def invites(self, interaction: discord.Interaction, membre: discord.Member = None):
        membre = membre or interaction.user
        try:
            invites = await interaction.guild.invites()
            user_invites = [inv for inv in invites if inv.inviter and inv.inviter.id == membre.id]
            total_uses = sum(inv.uses for inv in user_invites)
            embed = discord.Embed(title=f"📨 Invitations de {membre.display_name}", color=discord.Color.blurple())
            embed.add_field(name="Total d'invitations", value=str(len(user_invites)), inline=True)
            embed.add_field(name="Total d'utilisations", value=str(total_uses), inline=True)
            await interaction.response.send_message(embed=embed)
        except:
            await interaction.response.send_message("❌ Impossible de récupérer les invitations.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Fun(bot))
