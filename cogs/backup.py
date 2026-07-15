"""
Module Backup - Inspiré de : Xenon (sauvegarde/restauration de serveur)
Fonctionnalités : sauvegarder la structure d'un serveur (salons, rôles, catégories), restaurer
"""
import discord
from discord.ext import commands
from discord import app_commands
import json, os, datetime, asyncio

BACKUPS_FILE = "data/backups.json"

def load_backups():
    if os.path.exists(BACKUPS_FILE):
        with open(BACKUPS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_backups(data):
    with open(BACKUPS_FILE, "w") as f:
        json.dump(data, f, indent=2)

class Backup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="backup", description="Sauvegarder la structure du serveur (comme Xenon)")
    @app_commands.checks.has_permissions(administrator=True)
    async def backup(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        backup_data = {
            "name": guild.name,
            "icon": str(guild.icon.url) if guild.icon else None,
            "created_at": str(datetime.datetime.utcnow()),
            "roles": [],
            "categories": [],
            "channels": []
        }

        # Sauvegarder les rôles
        for role in guild.roles:
            if role.name == "@everyone":
                continue
            backup_data["roles"].append({
                "name": role.name,
                "color": role.color.value,
                "hoist": role.hoist,
                "mentionable": role.mentionable,
                "permissions": role.permissions.value,
                "position": role.position
            })

        # Sauvegarder les catégories
        for cat in guild.categories:
            cat_data = {
                "name": cat.name,
                "position": cat.position,
                "channels": []
            }
            for ch in cat.channels:
                ch_data = {
                    "name": ch.name,
                    "type": str(ch.type),
                    "position": ch.position,
                    "topic": getattr(ch, "topic", None),
                    "nsfw": getattr(ch, "nsfw", False),
                    "slowmode_delay": getattr(ch, "slowmode_delay", 0)
                }
                cat_data["channels"].append(ch_data)
            backup_data["categories"].append(cat_data)

        # Sauvegarder les salons sans catégorie
        for ch in guild.channels:
            if ch.category is None and not isinstance(ch, discord.CategoryChannel):
                backup_data["channels"].append({
                    "name": ch.name,
                    "type": str(ch.type),
                    "position": ch.position,
                    "topic": getattr(ch, "topic", None),
                    "nsfw": getattr(ch, "nsfw", False),
                    "slowmode_delay": getattr(ch, "slowmode_delay", 0)
                })

        backups = load_backups()
        backup_id = f"{guild.id}_{int(datetime.datetime.utcnow().timestamp())}"
        backups[backup_id] = backup_data
        save_backups(backups)

        embed = discord.Embed(title="✅ Sauvegarde Créée", color=discord.Color.green())
        embed.add_field(name="ID de sauvegarde", value=f"`{backup_id}`", inline=False)
        embed.add_field(name="Rôles sauvegardés", value=str(len(backup_data["roles"])), inline=True)
        embed.add_field(name="Catégories", value=str(len(backup_data["categories"])), inline=True)
        embed.add_field(name="Salons", value=str(len(backup_data["channels"])), inline=True)
        embed.set_footer(text="Utilisez /backupload <id> pour restaurer")
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="backuplist", description="Voir les sauvegardes disponibles")
    @app_commands.checks.has_permissions(administrator=True)
    async def backuplist(self, interaction: discord.Interaction):
        backups = load_backups()
        guild_backups = {k: v for k, v in backups.items() if k.startswith(str(interaction.guild.id))}
        embed = discord.Embed(title="📦 Sauvegardes Disponibles", color=discord.Color.blurple())
        if not guild_backups:
            embed.description = "Aucune sauvegarde trouvée."
        else:
            for bid, bdata in list(guild_backups.items())[-5:]:
                embed.add_field(
                    name=f"`{bid}`",
                    value=f"Créée le: {bdata['created_at'][:10]}\nRôles: {len(bdata['roles'])} | Catégories: {len(bdata['categories'])}",
                    inline=False
                )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="backupload", description="Restaurer une sauvegarde du serveur")
    @app_commands.describe(backup_id="L'ID de la sauvegarde à restaurer")
    @app_commands.checks.has_permissions(administrator=True)
    async def backupload(self, interaction: discord.Interaction, backup_id: str):
        await interaction.response.defer(ephemeral=True)
        backups = load_backups()
        if backup_id not in backups:
            await interaction.followup.send("❌ Sauvegarde introuvable.", ephemeral=True)
            return
        bdata = backups[backup_id]
        guild = interaction.guild
        restored = {"roles": 0, "categories": 0, "channels": 0}

        # Restaurer les rôles
        existing_role_names = [r.name for r in guild.roles]
        for role_data in sorted(bdata["roles"], key=lambda x: x["position"]):
            if role_data["name"] not in existing_role_names:
                try:
                    await guild.create_role(
                        name=role_data["name"],
                        color=discord.Color(role_data["color"]),
                        hoist=role_data["hoist"],
                        mentionable=role_data["mentionable"],
                        permissions=discord.Permissions(role_data["permissions"])
                    )
                    restored["roles"] += 1
                    await asyncio.sleep(0.5)
                except:
                    pass

        # Restaurer les catégories et salons
        for cat_data in bdata["categories"]:
            try:
                cat = await guild.create_category(cat_data["name"])
                restored["categories"] += 1
                for ch_data in cat_data["channels"]:
                    try:
                        if "text" in ch_data["type"]:
                            await guild.create_text_channel(
                                ch_data["name"],
                                category=cat,
                                topic=ch_data.get("topic"),
                                nsfw=ch_data.get("nsfw", False),
                                slowmode_delay=ch_data.get("slowmode_delay", 0)
                            )
                        elif "voice" in ch_data["type"]:
                            await guild.create_voice_channel(ch_data["name"], category=cat)
                        restored["channels"] += 1
                        await asyncio.sleep(0.3)
                    except:
                        pass
            except:
                pass

        embed = discord.Embed(title="✅ Sauvegarde Restaurée", color=discord.Color.green())
        embed.add_field(name="Rôles créés", value=str(restored["roles"]), inline=True)
        embed.add_field(name="Catégories créées", value=str(restored["categories"]), inline=True)
        embed.add_field(name="Salons créés", value=str(restored["channels"]), inline=True)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="backupdelete", description="Supprimer une sauvegarde")
    @app_commands.describe(backup_id="L'ID de la sauvegarde à supprimer")
    @app_commands.checks.has_permissions(administrator=True)
    async def backupdelete(self, interaction: discord.Interaction, backup_id: str):
        backups = load_backups()
        if backup_id in backups:
            del backups[backup_id]
            save_backups(backups)
            await interaction.response.send_message(f"✅ Sauvegarde `{backup_id}` supprimée.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Sauvegarde introuvable.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Backup(bot))
