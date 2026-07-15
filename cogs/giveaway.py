"""
Module Giveaway - Inspiré de : Giveaway Bot, Carl-bot, MEE6
Fonctionnalités : créer des giveaways, rejoindre, tirer au sort, reroll
"""
import discord
from discord.ext import commands
from discord import app_commands
import json, os, datetime, random, asyncio

GIVEAWAYS_FILE = "data/giveaways.json"

def load_giveaways():
    if os.path.exists(GIVEAWAYS_FILE):
        with open(GIVEAWAYS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_giveaways(data):
    with open(GIVEAWAYS_FILE, "w") as f:
        json.dump(data, f, indent=2)

class GiveawayView(discord.ui.View):
    def __init__(self, giveaway_id):
        super().__init__(timeout=None)
        self.giveaway_id = giveaway_id

    @discord.ui.button(label="🎉 Participer", style=discord.ButtonStyle.success, custom_id="join_giveaway")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        giveaways = load_giveaways()
        gid = str(interaction.guild.id)
        cid = str(interaction.channel.id)
        mid = str(interaction.message.id)
        key = f"{gid}_{cid}_{mid}"
        if key not in giveaways:
            await interaction.response.send_message("❌ Ce giveaway est introuvable.", ephemeral=True)
            return
        gw = giveaways[key]
        if gw.get("ended"):
            await interaction.response.send_message("❌ Ce giveaway est terminé.", ephemeral=True)
            return
        uid = str(interaction.user.id)
        if uid in gw["participants"]:
            gw["participants"].remove(uid)
            save_giveaways(giveaways)
            await interaction.response.send_message("✅ Tu t'es retiré du giveaway.", ephemeral=True)
        else:
            gw["participants"].append(uid)
            save_giveaways(giveaways)
            count = len(gw["participants"])
            await interaction.response.send_message(f"🎉 Tu participes au giveaway ! ({count} participants)", ephemeral=True)


class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def parse_duration(self, duration_str):
        """Parse '1h', '30m', '1d' etc."""
        units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        try:
            unit = duration_str[-1].lower()
            value = int(duration_str[:-1])
            return value * units.get(unit, 60)
        except:
            return 60

    @app_commands.command(name="gstart", description="Lancer un giveaway")
    @app_commands.describe(duree="Durée (ex: 1h, 30m, 1d)", gagnants="Nombre de gagnants", prix="Ce qu'on gagne")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def gstart(self, interaction: discord.Interaction, duree: str, gagnants: int, prix: str):
        seconds = self.parse_duration(duree)
        end_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds)
        embed = discord.Embed(
            title="🎉 GIVEAWAY 🎉",
            description=f"**Prix :** {prix}\n**Gagnants :** {gagnants}\n**Fin :** <t:{int(end_time.timestamp())}:R>\n\nClique sur 🎉 pour participer !",
            color=discord.Color.gold(),
            timestamp=end_time
        )
        embed.set_footer(text=f"Se termine le")
        await interaction.response.send_message("✅ Giveaway lancé !", ephemeral=True)
        msg = await interaction.channel.send(embed=embed)
        view = GiveawayView(str(msg.id))
        await msg.edit(view=view)
        giveaways = load_giveaways()
        key = f"{interaction.guild.id}_{interaction.channel.id}_{msg.id}"
        giveaways[key] = {
            "prize": prix,
            "winners_count": gagnants,
            "end_time": end_time.isoformat(),
            "participants": [],
            "ended": False,
            "channel_id": str(interaction.channel.id),
            "message_id": str(msg.id),
            "guild_id": str(interaction.guild.id)
        }
        save_giveaways(giveaways)
        await asyncio.sleep(seconds)
        await self.end_giveaway(interaction.guild, interaction.channel, msg.id, key)

    async def end_giveaway(self, guild, channel, message_id, key):
        giveaways = load_giveaways()
        if key not in giveaways:
            return
        gw = giveaways[key]
        if gw.get("ended"):
            return
        gw["ended"] = True
        save_giveaways(giveaways)
        participants = gw["participants"]
        winners_count = gw["winners_count"]
        prize = gw["prize"]
        try:
            msg = await channel.fetch_message(message_id)
        except:
            return
        if not participants:
            embed = discord.Embed(title="🎉 Giveaway Terminé", description=f"**Prix :** {prize}\n\nAucun participant. Pas de gagnant.", color=discord.Color.red())
            await msg.edit(embed=embed, view=None)
            await channel.send("😢 Personne n'a participé au giveaway.")
            return
        winners = random.sample(participants, min(winners_count, len(participants)))
        winner_mentions = " ".join([f"<@{w}>" for w in winners])
        embed = discord.Embed(title="🎉 Giveaway Terminé !", description=f"**Prix :** {prize}\n**Gagnant(s) :** {winner_mentions}", color=discord.Color.green())
        await msg.edit(embed=embed, view=None)
        await channel.send(f"🎉 Félicitations {winner_mentions} ! Vous avez gagné **{prize}** !")

    @app_commands.command(name="greroll", description="Relancer le tirage d'un giveaway terminé")
    @app_commands.describe(message_id="L'ID du message du giveaway")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def greroll(self, interaction: discord.Interaction, message_id: str):
        giveaways = load_giveaways()
        key = f"{interaction.guild.id}_{interaction.channel.id}_{message_id}"
        if key not in giveaways:
            await interaction.response.send_message("❌ Giveaway introuvable.", ephemeral=True)
            return
        gw = giveaways[key]
        participants = gw["participants"]
        if not participants:
            await interaction.response.send_message("❌ Aucun participant.", ephemeral=True)
            return
        winner = random.choice(participants)
        await interaction.response.send_message(f"🎉 Nouveau gagnant : <@{winner}> ! Félicitations pour **{gw['prize']}** !")

    @app_commands.command(name="gend", description="Terminer un giveaway prématurément")
    @app_commands.describe(message_id="L'ID du message du giveaway")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def gend(self, interaction: discord.Interaction, message_id: str):
        giveaways = load_giveaways()
        key = f"{interaction.guild.id}_{interaction.channel.id}_{message_id}"
        if key not in giveaways:
            await interaction.response.send_message("❌ Giveaway introuvable.", ephemeral=True)
            return
        await interaction.response.send_message("✅ Fin du giveaway en cours...", ephemeral=True)
        try:
            msg = await interaction.channel.fetch_message(int(message_id))
            await self.end_giveaway(interaction.guild, interaction.channel, int(message_id), key)
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur : {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
