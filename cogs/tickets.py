"""
Module Tickets - Inspiré de : Tickety, Helper.gg, Ticket Tool Pro, Carl-bot, MEE6
Fonctionnalités : création de tickets, panel de tickets, fermeture, transcription, catégories
"""
import discord
from discord.ext import commands
from discord import app_commands
import json, os, datetime

TICKETS_FILE = "data/tickets.json"

def load_tickets():
    if os.path.exists(TICKETS_FILE):
        with open(TICKETS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_tickets(data):
    with open(TICKETS_FILE, "w") as f:
        json.dump(data, f, indent=2)

class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Ouvrir un Ticket", style=discord.ButtonStyle.primary, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        tickets = load_tickets()
        gid = str(guild.id)
        uid = str(interaction.user.id)

        # Vérifier si l'utilisateur a déjà un ticket ouvert
        if gid in tickets:
            for ticket_id, ticket_data in tickets[gid].items():
                if ticket_data.get("user_id") == uid and ticket_data.get("status") == "open":
                    channel = guild.get_channel(int(ticket_id))
                    if channel:
                        await interaction.response.send_message(f"❌ Tu as déjà un ticket ouvert : {channel.mention}", ephemeral=True)
                        return

        # Créer la catégorie si elle n'existe pas
        category = discord.utils.get(guild.categories, name="🎫 Tickets")
        if not category:
            category = await guild.create_category("🎫 Tickets")

        # Créer le salon de ticket
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }
        # Ajouter les modérateurs
        for role in guild.roles:
            if role.permissions.manage_messages:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        channel = await guild.create_text_channel(
            f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites,
            topic=f"Ticket de {interaction.user} | ID: {interaction.user.id}"
        )

        # Enregistrer le ticket
        if gid not in tickets:
            tickets[gid] = {}
        tickets[gid][str(channel.id)] = {
            "user_id": uid,
            "user_name": str(interaction.user),
            "created_at": str(datetime.datetime.utcnow()),
            "status": "open"
        }
        save_tickets(tickets)

        # Message dans le ticket
        embed = discord.Embed(
            title="🎫 Ticket Ouvert",
            description=f"Bonjour {interaction.user.mention} ! L'équipe de support va vous répondre bientôt.\n\nDécrivez votre problème ci-dessous.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(text="Cliquez sur 🔒 pour fermer le ticket")
        view = CloseTicketView()
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"✅ Ticket créé : {channel.mention}", ephemeral=True)


class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Fermer le Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        tickets = load_tickets()
        gid = str(interaction.guild.id)
        cid = str(interaction.channel.id)

        if gid in tickets and cid in tickets[gid]:
            tickets[gid][cid]["status"] = "closed"
            tickets[gid][cid]["closed_by"] = str(interaction.user)
            tickets[gid][cid]["closed_at"] = str(datetime.datetime.utcnow())
            save_tickets(tickets)

        # Générer la transcription
        messages = []
        async for msg in interaction.channel.history(limit=200, oldest_first=True):
            if not msg.author.bot:
                messages.append(f"[{msg.created_at.strftime('%H:%M:%S')}] {msg.author}: {msg.content}")

        transcript = "\n".join(messages)

        embed = discord.Embed(title="🔒 Ticket Fermé", description=f"Fermé par {interaction.user.mention}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)

        # Envoyer la transcription en DM
        ticket_data = tickets.get(gid, {}).get(cid, {})
        user_id = ticket_data.get("user_id")
        if user_id:
            try:
                user = await interaction.guild.fetch_member(int(user_id))
                dm_embed = discord.Embed(title="📋 Transcription de votre ticket", color=discord.Color.blurple())
                dm_embed.description = transcript[:4000] if transcript else "Aucun message."
                await user.send(embed=dm_embed)
            except:
                pass

        import asyncio
        await asyncio.sleep(5)
        await interaction.channel.delete()


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(TicketButton())
        self.bot.add_view(CloseTicketView())

    @app_commands.command(name="ticketpanel", description="Créer un panel de tickets dans ce salon")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticketpanel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎫 Support — Ouvrir un Ticket",
            description="Cliquez sur le bouton ci-dessous pour ouvrir un ticket de support.\nNotre équipe vous répondra dans les plus brefs délais.",
            color=discord.Color.blurple()
        )
        embed.set_footer(text=interaction.guild.name)
        if interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)
        view = TicketButton()
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ Panel de tickets créé.", ephemeral=True)

    @app_commands.command(name="addticket", description="Ajouter un utilisateur à ce ticket")
    @app_commands.describe(membre="Le membre à ajouter")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def addticket(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.channel.set_permissions(membre, read_messages=True, send_messages=True)
        await interaction.response.send_message(f"✅ {membre.mention} ajouté au ticket.")

    @app_commands.command(name="removeticket", description="Retirer un utilisateur de ce ticket")
    @app_commands.describe(membre="Le membre à retirer")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def removeticket(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.channel.set_permissions(membre, read_messages=False)
        await interaction.response.send_message(f"✅ {membre.mention} retiré du ticket.")

    @app_commands.command(name="tickets", description="Voir les tickets ouverts du serveur")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def list_tickets(self, interaction: discord.Interaction):
        tickets = load_tickets()
        gid = str(interaction.guild.id)
        guild_tickets = tickets.get(gid, {})
        open_tickets = [(cid, t) for cid, t in guild_tickets.items() if t.get("status") == "open"]
        embed = discord.Embed(title="🎫 Tickets Ouverts", color=discord.Color.blurple())
        if not open_tickets:
            embed.description = "Aucun ticket ouvert."
        else:
            for cid, t in open_tickets[:10]:
                channel = interaction.guild.get_channel(int(cid))
                embed.add_field(
                    name=f"#{channel.name if channel else cid}",
                    value=f"Ouvert par: {t['user_name']}\nDate: {t['created_at'][:10]}",
                    inline=True
                )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
