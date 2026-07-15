"""
Module Identité — /transform <nomdubot> et /reset
Utilise une seule commande slash avec autocomplétion pour respecter la limite de 100 commandes Discord.

Supporte désormais 1000+ identités de bots.
"""

import discord
from discord.ext import commands
from discord import app_commands
import aiohttp, json, os
from typing import List, Dict, Any

async def download_avatar(url: str) -> bytes | None:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 200:
                    return await resp.read()
    except Exception:
        pass
    return None

class Identity(commands.Cog):
    """Cog qui gère le changement d'identité du bot via /transform et /reset."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._original_name: str | None = None
        self._original_avatar: bytes | None = None

    @property
    def extras(self):
        return self.bot.extras

    async def _ensure_original_saved(self):
        if self._original_name is None:
            self._original_name = self.bot.user.name
        if self._original_avatar is None and self.bot.user.avatar:
            self._original_avatar = await download_avatar(self.bot.user.avatar.url)

    async def _apply_identity(self, key: str):
        data = self.extras["bots_data"][key]
        try:
            await self.bot.user.edit(username=data["name"])
        except discord.HTTPException:
            pass
        avatar_bytes = await download_avatar(data["avatar"])
        if avatar_bytes:
            try:
                await self.bot.user.edit(avatar=avatar_bytes)
            except discord.HTTPException:
                pass
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name=data["status"]
            ),
            status=discord.Status.online
        )

    # ── Autocomplétion ────────────────────────────────────────────────────────
    async def bot_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        choices = []
        for key, data in self.extras["bots_data"].items():
            if current.lower() in key.lower() or current.lower() in data["name"].lower():
                choices.append(app_commands.Choice(name=data["name"], value=key))
            if len(choices) >= 25: # Limite Discord pour l'autocomplétion
                break
        return choices

    # ── /transform ────────────────────────────────────────────────────────────
    @app_commands.command(
        name="transform",
        description="Transformer le bot en un autre bot (MEE6, Dyno, Wick, Clyde...)"
    )
    @app_commands.describe(nomdubot="Nom du bot à imiter (ex: mee6, dyno, wick, clyde...)")
    @app_commands.autocomplete(nomdubot=bot_autocomplete)
    @app_commands.checks.has_permissions(administrator=True)
    async def transform(self, interaction: discord.Interaction, nomdubot: str):
        key = nomdubot.lower().strip()
        if key not in self.extras["bots_data"]:
            available = ", ".join(f"`{k}`" for k in list(self.extras["bots_data"].keys())[:12])
            await interaction.response.send_message(
                f"❌ Bot `{nomdubot}` inconnu.\nUtilise `/botlist` pour voir tous les bots disponibles.\n**Exemples :** {available}...",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)
        await self._ensure_original_saved()
        await self._apply_identity(key)
        
        self.extras["guild_identities"][str(interaction.guild.id)] = key
        self.extras["save_json_file"](self.extras["identity_file"], self.extras["guild_identities"])
        self.extras["update_guild_active_commands"](interaction.guild.id, key)
        
        # Note: Syncing commands for a guild can be slow, but it helps updating the visual list
        try:
            await self.bot.tree.sync(guild=interaction.guild)
        except:
            pass

        data = self.extras["bots_data"][key]
        embed = discord.Embed(
            title=f"✅ Identité changée → {data["name"]}",
            description=data["description"],
            color=discord.Color(data["color"])
        )
        embed.add_field(name="💡 Commandes disponibles", value=data["commands_hint"], inline=False)
        embed.add_field(
            name="↩️ Revenir à la normale",
            value="Utilise `/reset` pour restaurer l'identité d'origine.",
            inline=False
        )
        embed.set_footer(text=f"Demandé par {interaction.user.display_name}")
        await interaction.followup.send(embed=embed, ephemeral=True)

        pub = discord.Embed(
            title=f"🔄 Le bot est maintenant **{data["name"]}** !",
            description=data["description"],
            color=discord.Color(data["color"])
        )
        pub.add_field(name="Commandes", value=data["commands_hint"], inline=False)
        pub.set_footer(text="Utilise /reset pour revenir à la normale")
        await interaction.channel.send(embed=pub)

    # ── /reset ────────────────────────────────────────────────────────────────
    @app_commands.command(name="reset", description="Revenir à l'identité originale du bot")
    @app_commands.checks.has_permissions(administrator=True)
    async def reset(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await self._ensure_original_saved()

        original_name = self._original_name or "UltraBot"
        try:
            await self.bot.user.edit(username=original_name)
        except discord.HTTPException:
            pass
        if self._original_avatar:
            try:
                await self.bot.user.edit(avatar=self._original_avatar)
            except discord.HTTPException:
                pass

        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"/help | {len(self.bot.guilds)} serveurs"
            ),
            status=discord.Status.online
        )
        self.extras["guild_identities"].pop(str(interaction.guild.id), None)
        self.extras["save_json_file"](self.extras["identity_file"], self.extras["guild_identities"])
        self.extras["update_guild_active_commands"](interaction.guild.id, None)
        
        try:
            await self.bot.tree.sync(guild=interaction.guild)
        except:
            pass

        await interaction.followup.send(
            embed=discord.Embed(
                title="✅ Identité réinitialisée !",
                description=f"Le bot est revenu à son identité d'origine : **{original_name}**.",
                color=discord.Color.blurple()
            ),
            ephemeral=True
        )
        await interaction.channel.send(
            embed=discord.Embed(
                title="🔄 Retour à la normale !",
                description=f"Le bot est de nouveau **{original_name}**. Utilise `/help` pour toutes les commandes.",
                color=discord.Color.blurple()
            )
        )

    # ── /botlist ──────────────────────────────────────────────────────────────
    @app_commands.command(name="botlist", description="Voir tous les bots disponibles pour l'imitation")
    async def botlist(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🤖 Bots Disponibles",
            description="Utilise `/transform <nomdubot>` pour changer d'identité.\nUtilise `/reset` pour revenir à la normale.\n\n**Liste partielle (1000+ bots disponibles via autocomplétion) :**",
            color=discord.Color.blurple()
        )
        # Afficher seulement les 20 premiers pour ne pas surcharger le message
        lines = [f"`{k}` → **{v["name"]}**" for k, v in list(self.extras["bots_data"].items())[:20]]
        embed.add_field(name="Bots", value="\n".join(lines), inline=False)
        embed.set_footer(text=f"{len(self.extras["bots_data"])} bots disponibles | /reset pour revenir à la normale")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Identity(bot))
