"""
Module Musique - Inspiré de : FredBoat, Pancake, Cloudy, Nik, Cinebot
Fonctionnalités : play, pause, resume, skip, queue, volume, nowplaying, stop, leave
Note : Nécessite yt-dlp et ffmpeg installés
"""
import discord
from discord.ext import commands
from discord import app_commands
import asyncio, json, os

try:
    import yt_dlp as youtube_dl
    YDL_AVAILABLE = True
except ImportError:
    YDL_AVAILABLE = False

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0'
}

class MusicQueue:
    def __init__(self):
        self.queue = []
        self.current = None
        self.volume = 0.5
        self.loop = False

music_queues = {}

def get_queue(guild_id):
    if guild_id not in music_queues:
        music_queues[guild_id] = MusicQueue()
    return music_queues[guild_id]

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_audio_source(self, query):
        if not YDL_AVAILABLE:
            return None, "yt-dlp non installé"
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                if not query.startswith("http"):
                    query = f"ytsearch:{query}"
                info = ydl.extract_info(query, download=False)
                if 'entries' in info:
                    info = info['entries'][0]
                url = info['url']
                title = info.get('title', 'Inconnu')
                duration = info.get('duration', 0)
                thumbnail = info.get('thumbnail', None)
                return {"url": url, "title": title, "duration": duration, "thumbnail": thumbnail}, None
            except Exception as e:
                return None, str(e)

    async def play_next(self, guild_id, voice_client):
        queue = get_queue(guild_id)
        if queue.loop and queue.current:
            track = queue.current
        elif queue.queue:
            track = queue.queue.pop(0)
            queue.current = track
        else:
            queue.current = None
            return
        try:
            source = discord.FFmpegPCMAudio(track["url"], **FFMPEG_OPTIONS)
            source = discord.PCMVolumeTransformer(source, volume=queue.volume)
            def after_play(error):
                asyncio.run_coroutine_threadsafe(self.play_next(guild_id, voice_client), self.bot.loop)
            voice_client.play(source, after=after_play)
        except Exception as e:
            print(f"Erreur lecture : {e}")

    @app_commands.command(name="play", description="Jouer une musique (YouTube)")
    @app_commands.describe(query="Nom de la musique ou URL YouTube")
    async def play(self, interaction: discord.Interaction, query: str):
        if not interaction.user.voice:
            await interaction.response.send_message("❌ Tu dois être dans un salon vocal.", ephemeral=True)
            return
        if not YDL_AVAILABLE:
            await interaction.response.send_message("❌ Module yt-dlp non disponible. Installe-le avec `pip install yt-dlp`.", ephemeral=True)
            return
        await interaction.response.defer()
        voice_channel = interaction.user.voice.channel
        voice_client = interaction.guild.voice_client
        if not voice_client:
            voice_client = await voice_channel.connect()
        elif voice_client.channel != voice_channel:
            await voice_client.move_to(voice_channel)
        track, error = await self.get_audio_source(query)
        if error:
            await interaction.followup.send(f"❌ Erreur : {error}")
            return
        queue = get_queue(interaction.guild.id)
        queue.queue.append(track)
        if not voice_client.is_playing():
            await self.play_next(interaction.guild.id, voice_client)
            embed = discord.Embed(title="▶️ Lecture en cours", color=discord.Color.green())
        else:
            embed = discord.Embed(title="📋 Ajouté à la file", color=discord.Color.blurple())
        embed.add_field(name="Titre", value=track["title"], inline=False)
        mins, secs = divmod(track["duration"], 60)
        embed.add_field(name="Durée", value=f"{mins}:{secs:02d}", inline=True)
        embed.add_field(name="File d'attente", value=str(len(queue.queue)), inline=True)
        if track["thumbnail"]:
            embed.set_thumbnail(url=track["thumbnail"])
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="pause", description="Mettre la musique en pause")
    async def pause(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸️ Musique en pause.")
        else:
            await interaction.response.send_message("❌ Aucune musique en cours.", ephemeral=True)

    @app_commands.command(name="resume", description="Reprendre la musique")
    async def resume(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶️ Musique reprise.")
        else:
            await interaction.response.send_message("❌ Aucune musique en pause.", ephemeral=True)

    @app_commands.command(name="skip", description="Passer à la prochaine musique")
    async def skip(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await interaction.response.send_message("⏭️ Musique passée.")
        else:
            await interaction.response.send_message("❌ Aucune musique en cours.", ephemeral=True)

    @app_commands.command(name="stop", description="Arrêter la musique et vider la file")
    async def stop(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc:
            queue = get_queue(interaction.guild.id)
            queue.queue.clear()
            queue.current = None
            vc.stop()
            await interaction.response.send_message("⏹️ Musique arrêtée et file vidée.")
        else:
            await interaction.response.send_message("❌ Pas de connexion vocale.", ephemeral=True)

    @app_commands.command(name="leave", description="Faire quitter le bot du salon vocal")
    async def leave(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc:
            queue = get_queue(interaction.guild.id)
            queue.queue.clear()
            queue.current = None
            await vc.disconnect()
            await interaction.response.send_message("👋 Bot déconnecté du salon vocal.")
        else:
            await interaction.response.send_message("❌ Pas de connexion vocale.", ephemeral=True)

    @app_commands.command(name="queue", description="Voir la file d'attente musicale")
    async def queue_cmd(self, interaction: discord.Interaction):
        queue = get_queue(interaction.guild.id)
        embed = discord.Embed(title="📋 File d'attente", color=discord.Color.blurple())
        if queue.current:
            embed.add_field(name="▶️ En cours", value=queue.current["title"], inline=False)
        if queue.queue:
            tracks = "\n".join([f"**{i+1}.** {t['title']}" for i, t in enumerate(queue.queue[:10])])
            embed.add_field(name=f"Suivants ({len(queue.queue)})", value=tracks, inline=False)
        else:
            embed.add_field(name="File vide", value="Aucune musique en attente.", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="volume", description="Régler le volume (0-100)")
    @app_commands.describe(niveau="Volume de 0 à 100")
    async def volume(self, interaction: discord.Interaction, niveau: int):
        if niveau < 0 or niveau > 100:
            await interaction.response.send_message("❌ Volume entre 0 et 100.", ephemeral=True)
            return
        queue = get_queue(interaction.guild.id)
        queue.volume = niveau / 100
        vc = interaction.guild.voice_client
        if vc and vc.source:
            vc.source.volume = queue.volume
        await interaction.response.send_message(f"🔊 Volume réglé à **{niveau}%**.")

    @app_commands.command(name="nowplaying", description="Voir la musique en cours")
    async def nowplaying(self, interaction: discord.Interaction):
        queue = get_queue(interaction.guild.id)
        if not queue.current:
            await interaction.response.send_message("❌ Aucune musique en cours.", ephemeral=True)
            return
        track = queue.current
        embed = discord.Embed(title="🎵 En cours de lecture", color=discord.Color.green())
        embed.add_field(name="Titre", value=track["title"], inline=False)
        mins, secs = divmod(track["duration"], 60)
        embed.add_field(name="Durée", value=f"{mins}:{secs:02d}", inline=True)
        embed.add_field(name="Volume", value=f"{int(queue.volume * 100)}%", inline=True)
        embed.add_field(name="Boucle", value="✅" if queue.loop else "❌", inline=True)
        if track.get("thumbnail"):
            embed.set_thumbnail(url=track["thumbnail"])
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="loop", description="Activer/désactiver la boucle")
    async def loop(self, interaction: discord.Interaction):
        queue = get_queue(interaction.guild.id)
        queue.loop = not queue.loop
        status = "✅ activée" if queue.loop else "❌ désactivée"
        await interaction.response.send_message(f"🔁 Boucle {status}.")

async def setup(bot):
    await bot.add_cog(Music(bot))
