"""
Module Économie - Inspiré de : Dank Memer, OwO, MEE6 (niveaux), Mimu, Dark Memer
Fonctionnalités : monnaie, daily, work, shop, balance, leaderboard, niveaux XP, récompenses
"""
import discord
from discord.ext import commands
from discord import app_commands
import json, os, datetime, random

ECONOMY_FILE = "data/economy.json"
LEVELS_FILE = "data/levels.json"

def load_economy():
    if os.path.exists(ECONOMY_FILE):
        with open(ECONOMY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_economy(data):
    with open(ECONOMY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_levels():
    if os.path.exists(LEVELS_FILE):
        with open(LEVELS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_levels(data):
    with open(LEVELS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_user_eco(data, guild_id, user_id):
    gid, uid = str(guild_id), str(user_id)
    if gid not in data:
        data[gid] = {}
    if uid not in data[gid]:
        data[gid][uid] = {"balance": 0, "bank": 0, "last_daily": None, "last_work": None, "inventory": []}
    return data[gid][uid]

def xp_for_level(level):
    return 5 * (level ** 2) + 50 * level + 100

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── BALANCE ───────────────────────────────────────────────────────────────
    @app_commands.command(name="balance", description="Voir votre solde ou celui d'un membre")
    @app_commands.describe(membre="Le membre (optionnel)")
    async def balance(self, interaction: discord.Interaction, membre: discord.Member = None):
        membre = membre or interaction.user
        eco = load_economy()
        user = get_user_eco(eco, interaction.guild.id, membre.id)
        embed = discord.Embed(title=f"💰 Solde de {membre.display_name}", color=discord.Color.gold())
        embed.add_field(name="Portefeuille", value=f"🪙 {user['balance']:,}", inline=True)
        embed.add_field(name="Banque", value=f"🏦 {user['bank']:,}", inline=True)
        embed.add_field(name="Total", value=f"💎 {user['balance'] + user['bank']:,}", inline=True)
        embed.set_thumbnail(url=membre.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    # ── DAILY ─────────────────────────────────────────────────────────────────
    @app_commands.command(name="daily", description="Récupérer votre récompense quotidienne")
    async def daily(self, interaction: discord.Interaction):
        eco = load_economy()
        user = get_user_eco(eco, interaction.guild.id, interaction.user.id)
        now = datetime.datetime.utcnow()
        last = user.get("last_daily")
        if last:
            last_dt = datetime.datetime.fromisoformat(last)
            diff = (now - last_dt).total_seconds()
            if diff < 86400:
                remaining = 86400 - diff
                h, m = int(remaining // 3600), int((remaining % 3600) // 60)
                await interaction.response.send_message(f"⏰ Déjà récupéré ! Reviens dans **{h}h {m}m**.", ephemeral=True)
                return
        reward = random.randint(100, 500)
        streak_bonus = random.randint(0, 100)
        total = reward + streak_bonus
        user["balance"] += total
        user["last_daily"] = now.isoformat()
        save_economy(eco)
        embed = discord.Embed(title="🎁 Récompense Quotidienne", color=discord.Color.green())
        embed.add_field(name="Récompense", value=f"🪙 +{reward}", inline=True)
        embed.add_field(name="Bonus", value=f"✨ +{streak_bonus}", inline=True)
        embed.add_field(name="Total reçu", value=f"💰 +{total}", inline=True)
        embed.add_field(name="Nouveau solde", value=f"🪙 {user['balance']:,}", inline=False)
        await interaction.response.send_message(embed=embed)

    # ── WORK ──────────────────────────────────────────────────────────────────
    @app_commands.command(name="work", description="Travailler pour gagner des pièces")
    async def work(self, interaction: discord.Interaction):
        eco = load_economy()
        user = get_user_eco(eco, interaction.guild.id, interaction.user.id)
        now = datetime.datetime.utcnow()
        last = user.get("last_work")
        if last:
            last_dt = datetime.datetime.fromisoformat(last)
            diff = (now - last_dt).total_seconds()
            if diff < 3600:
                remaining = 3600 - diff
                m = int(remaining // 60)
                await interaction.response.send_message(f"⏰ Tu es fatigué ! Reviens dans **{m} minutes**.", ephemeral=True)
                return
        jobs = [
            ("Développeur", 200, 400), ("Médecin", 300, 600), ("Cuisinier", 150, 300),
            ("Livreur", 100, 250), ("Professeur", 200, 350), ("Artiste", 150, 450),
            ("Ingénieur", 250, 500), ("Pompier", 200, 400), ("Pilote", 300, 700)
        ]
        job, min_pay, max_pay = random.choice(jobs)
        earned = random.randint(min_pay, max_pay)
        user["balance"] += earned
        user["last_work"] = now.isoformat()
        save_economy(eco)
        embed = discord.Embed(title="💼 Travail", color=discord.Color.blue())
        embed.description = f"Tu as travaillé comme **{job}** et gagné **🪙 {earned}** pièces !"
        embed.add_field(name="Nouveau solde", value=f"🪙 {user['balance']:,}", inline=False)
        await interaction.response.send_message(embed=embed)

    # ── DEPOSIT ───────────────────────────────────────────────────────────────
    @app_commands.command(name="deposit", description="Déposer des pièces à la banque")
    @app_commands.describe(montant="Montant à déposer (ou 'all')")
    async def deposit(self, interaction: discord.Interaction, montant: str):
        eco = load_economy()
        user = get_user_eco(eco, interaction.guild.id, interaction.user.id)
        if montant.lower() == "all":
            amount = user["balance"]
        else:
            try:
                amount = int(montant)
            except:
                await interaction.response.send_message("❌ Montant invalide.", ephemeral=True)
                return
        if amount <= 0 or amount > user["balance"]:
            await interaction.response.send_message("❌ Montant invalide ou insuffisant.", ephemeral=True)
            return
        user["balance"] -= amount
        user["bank"] += amount
        save_economy(eco)
        await interaction.response.send_message(f"✅ **🪙 {amount:,}** déposés à la banque.")

    # ── WITHDRAW ──────────────────────────────────────────────────────────────
    @app_commands.command(name="withdraw", description="Retirer des pièces de la banque")
    @app_commands.describe(montant="Montant à retirer (ou 'all')")
    async def withdraw(self, interaction: discord.Interaction, montant: str):
        eco = load_economy()
        user = get_user_eco(eco, interaction.guild.id, interaction.user.id)
        if montant.lower() == "all":
            amount = user["bank"]
        else:
            try:
                amount = int(montant)
            except:
                await interaction.response.send_message("❌ Montant invalide.", ephemeral=True)
                return
        if amount <= 0 or amount > user["bank"]:
            await interaction.response.send_message("❌ Montant invalide ou insuffisant.", ephemeral=True)
            return
        user["bank"] -= amount
        user["balance"] += amount
        save_economy(eco)
        await interaction.response.send_message(f"✅ **🪙 {amount:,}** retirés de la banque.")

    # ── PAY ───────────────────────────────────────────────────────────────────
    @app_commands.command(name="pay", description="Donner des pièces à un autre membre")
    @app_commands.describe(membre="Le destinataire", montant="Montant à donner")
    async def pay(self, interaction: discord.Interaction, membre: discord.Member, montant: int):
        if membre.id == interaction.user.id:
            await interaction.response.send_message("❌ Tu ne peux pas te payer toi-même.", ephemeral=True)
            return
        eco = load_economy()
        sender = get_user_eco(eco, interaction.guild.id, interaction.user.id)
        receiver = get_user_eco(eco, interaction.guild.id, membre.id)
        if montant <= 0 or montant > sender["balance"]:
            await interaction.response.send_message("❌ Montant invalide ou insuffisant.", ephemeral=True)
            return
        sender["balance"] -= montant
        receiver["balance"] += montant
        save_economy(eco)
        await interaction.response.send_message(f"✅ Tu as donné **🪙 {montant:,}** à {membre.mention}.")

    # ── LEADERBOARD ───────────────────────────────────────────────────────────
    @app_commands.command(name="leaderboard", description="Voir le classement économique du serveur")
    async def leaderboard(self, interaction: discord.Interaction):
        eco = load_economy()
        gid = str(interaction.guild.id)
        guild_data = eco.get(gid, {})
        sorted_users = sorted(guild_data.items(), key=lambda x: x[1]["balance"] + x[1]["bank"], reverse=True)[:10]
        embed = discord.Embed(title="🏆 Classement Économique", color=discord.Color.gold())
        medals = ["🥇", "🥈", "🥉"]
        for i, (uid, data) in enumerate(sorted_users):
            member = interaction.guild.get_member(int(uid))
            name = member.display_name if member else f"Utilisateur {uid}"
            medal = medals[i] if i < 3 else f"**#{i+1}**"
            total = data["balance"] + data["bank"]
            embed.add_field(name=f"{medal} {name}", value=f"🪙 {total:,}", inline=False)
        await interaction.response.send_message(embed=embed)

    # ── GAMBLE ────────────────────────────────────────────────────────────────
    @app_commands.command(name="gamble", description="Parier des pièces (50% de chance)")
    @app_commands.describe(montant="Montant à parier")
    async def gamble(self, interaction: discord.Interaction, montant: int):
        eco = load_economy()
        user = get_user_eco(eco, interaction.guild.id, interaction.user.id)
        if montant <= 0 or montant > user["balance"]:
            await interaction.response.send_message("❌ Montant invalide ou insuffisant.", ephemeral=True)
            return
        win = random.random() > 0.5
        if win:
            user["balance"] += montant
            save_economy(eco)
            await interaction.response.send_message(f"🎰 Tu as **gagné** 🪙 {montant:,} ! Nouveau solde : 🪙 {user['balance']:,}")
        else:
            user["balance"] -= montant
            save_economy(eco)
            await interaction.response.send_message(f"🎰 Tu as **perdu** 🪙 {montant:,}... Nouveau solde : 🪙 {user['balance']:,}")

    # ── NIVEAUX XP ────────────────────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        levels = load_levels()
        gid, uid = str(message.guild.id), str(message.author.id)
        if gid not in levels:
            levels[gid] = {}
        if uid not in levels[gid]:
            levels[gid][uid] = {"xp": 0, "level": 0}
        xp_gain = random.randint(15, 25)
        levels[gid][uid]["xp"] += xp_gain
        current_level = levels[gid][uid]["level"]
        xp_needed = xp_for_level(current_level)
        if levels[gid][uid]["xp"] >= xp_needed:
            levels[gid][uid]["level"] += 1
            levels[gid][uid]["xp"] -= xp_needed
            new_level = levels[gid][uid]["level"]
            save_levels(levels)
            embed = discord.Embed(title="🎉 Niveau Supérieur !", color=discord.Color.gold())
            embed.description = f"Félicitations {message.author.mention} ! Tu es maintenant **niveau {new_level}** !"
            await message.channel.send(embed=embed)
        else:
            save_levels(levels)

    @app_commands.command(name="rank", description="Voir votre niveau ou celui d'un membre")
    @app_commands.describe(membre="Le membre (optionnel)")
    async def rank(self, interaction: discord.Interaction, membre: discord.Member = None):
        membre = membre or interaction.user
        levels = load_levels()
        gid, uid = str(interaction.guild.id), str(membre.id)
        user_data = levels.get(gid, {}).get(uid, {"xp": 0, "level": 0})
        level = user_data["level"]
        xp = user_data["xp"]
        xp_needed = xp_for_level(level)
        progress = int((xp / xp_needed) * 20)
        bar = "█" * progress + "░" * (20 - progress)
        embed = discord.Embed(title=f"⭐ Niveau de {membre.display_name}", color=discord.Color.gold())
        embed.set_thumbnail(url=membre.display_avatar.url)
        embed.add_field(name="Niveau", value=f"**{level}**", inline=True)
        embed.add_field(name="XP", value=f"{xp}/{xp_needed}", inline=True)
        embed.add_field(name="Progression", value=f"`{bar}`", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="levelboard", description="Classement des niveaux du serveur")
    async def levelboard(self, interaction: discord.Interaction):
        levels = load_levels()
        gid = str(interaction.guild.id)
        guild_data = levels.get(gid, {})
        sorted_users = sorted(guild_data.items(), key=lambda x: (x[1]["level"], x[1]["xp"]), reverse=True)[:10]
        embed = discord.Embed(title="⭐ Classement des Niveaux", color=discord.Color.gold())
        medals = ["🥇", "🥈", "🥉"]
        for i, (uid, data) in enumerate(sorted_users):
            member = interaction.guild.get_member(int(uid))
            name = member.display_name if member else f"Utilisateur {uid}"
            medal = medals[i] if i < 3 else f"**#{i+1}**"
            embed.add_field(name=f"{medal} {name}", value=f"Niveau **{data['level']}** — {data['xp']} XP", inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))
