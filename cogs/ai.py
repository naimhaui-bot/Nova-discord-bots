"""
Module IA - Inspiré de : Clyde (Discord AI), MEE6 IA Creator, Coach from Rec Room, OpenAI Bot
Fonctionnalités : chat IA, génération d'images (Midjourney-like), résumé, traduction, correction
"""
import discord
from discord.ext import commands
from discord import app_commands
import os, json, asyncio

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

AI_CONFIG_FILE = "data/ai_config.json"

def load_ai_config():
    if os.path.exists(AI_CONFIG_FILE):
        with open(AI_CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_ai_config(data):
    with open(AI_CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conversations = {}  # user_id -> [messages]
        if OPENAI_AVAILABLE:
            self.client = AsyncOpenAI(
                api_key=os.environ.get("OPENAI_API_KEY", ""),
                base_url=os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
            )

    async def get_ai_response(self, user_id, message, system_prompt=None):
        if not OPENAI_AVAILABLE:
            return "❌ Module OpenAI non disponible."
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        if system_prompt is None:
            system_prompt = "Tu es un assistant Discord utile, amical et intelligent. Réponds en français de manière concise et claire."
        self.conversations[user_id].append({"role": "user", "content": message})
        # Garder seulement les 10 derniers messages
        if len(self.conversations[user_id]) > 20:
            self.conversations[user_id] = self.conversations[user_id][-20:]
        messages = [{"role": "system", "content": system_prompt}] + self.conversations[user_id]
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            reply = response.choices[0].message.content
            self.conversations[user_id].append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            return f"❌ Erreur IA : {str(e)}"

    # ── CHAT IA ───────────────────────────────────────────────────────────────
    @app_commands.command(name="ask", description="Poser une question à l'IA (comme Clyde)")
    @app_commands.describe(question="Ta question pour l'IA")
    async def ask(self, interaction: discord.Interaction, question: str):
        await interaction.response.defer()
        response = await self.get_ai_response(str(interaction.user.id), question)
        embed = discord.Embed(title="🤖 Assistant IA", color=discord.Color.blurple())
        embed.add_field(name="Question", value=question[:1024], inline=False)
        # Découper la réponse si trop longue
        if len(response) > 1024:
            parts = [response[i:i+1024] for i in range(0, len(response), 1024)]
            embed.add_field(name="Réponse", value=parts[0], inline=False)
            for part in parts[1:]:
                embed.add_field(name="(suite)", value=part, inline=False)
        else:
            embed.add_field(name="Réponse", value=response, inline=False)
        embed.set_footer(text=f"Demandé par {interaction.user.display_name}")
        await interaction.followup.send(embed=embed)

    # ── RESET CONVERSATION ────────────────────────────────────────────────────
    @app_commands.command(name="resetai", description="Réinitialiser la conversation avec l'IA")
    async def resetai(self, interaction: discord.Interaction):
        uid = str(interaction.user.id)
        if uid in self.conversations:
            self.conversations[uid] = []
        await interaction.response.send_message("✅ Conversation réinitialisée.", ephemeral=True)

    # ── TRANSLATE ─────────────────────────────────────────────────────────────
    @app_commands.command(name="translate", description="Traduire un texte")
    @app_commands.describe(texte="Le texte à traduire", langue="La langue cible (ex: anglais, espagnol)")
    async def translate(self, interaction: discord.Interaction, texte: str, langue: str = "anglais"):
        await interaction.response.defer()
        prompt = f"Traduis ce texte en {langue}, réponds UNIQUEMENT avec la traduction sans explication :\n\n{texte}"
        response = await self.get_ai_response(f"translate_{interaction.user.id}", prompt,
            system_prompt="Tu es un traducteur professionnel. Traduis uniquement, sans ajouter de commentaires.")
        embed = discord.Embed(title="🌍 Traduction", color=discord.Color.green())
        embed.add_field(name="Texte original", value=texte[:1024], inline=False)
        embed.add_field(name=f"Traduction ({langue})", value=response[:1024], inline=False)
        await interaction.followup.send(embed=embed)

    # ── SUMMARIZE ─────────────────────────────────────────────────────────────
    @app_commands.command(name="summarize", description="Résumer un texte avec l'IA")
    @app_commands.describe(texte="Le texte à résumer")
    async def summarize(self, interaction: discord.Interaction, texte: str):
        await interaction.response.defer()
        prompt = f"Résume ce texte en 3-5 phrases courtes en français :\n\n{texte}"
        response = await self.get_ai_response(f"sum_{interaction.user.id}", prompt,
            system_prompt="Tu es un expert en résumé. Sois concis et précis.")
        embed = discord.Embed(title="📝 Résumé", color=discord.Color.orange())
        embed.add_field(name="Résumé", value=response[:1024], inline=False)
        await interaction.followup.send(embed=embed)

    # ── CORRECT ───────────────────────────────────────────────────────────────
    @app_commands.command(name="correct", description="Corriger un texte avec l'IA")
    @app_commands.describe(texte="Le texte à corriger")
    async def correct(self, interaction: discord.Interaction, texte: str):
        await interaction.response.defer()
        prompt = f"Corrige les fautes d'orthographe et de grammaire dans ce texte. Réponds avec le texte corrigé uniquement :\n\n{texte}"
        response = await self.get_ai_response(f"correct_{interaction.user.id}", prompt,
            system_prompt="Tu es un correcteur professionnel. Corrige uniquement les fautes, sans changer le sens.")
        embed = discord.Embed(title="✏️ Correction", color=discord.Color.green())
        embed.add_field(name="Texte original", value=texte[:512], inline=False)
        embed.add_field(name="Texte corrigé", value=response[:512], inline=False)
        await interaction.followup.send(embed=embed)

    # ── IMAGINE (Midjourney-like) ─────────────────────────────────────────────
    @app_commands.command(name="imagine", description="Générer une image avec l'IA (Midjourney-like)")
    @app_commands.describe(prompt="Description de l'image à générer")
    async def imagine(self, interaction: discord.Interaction, prompt: str):
        await interaction.response.defer()
        if not OPENAI_AVAILABLE:
            await interaction.followup.send("❌ Module OpenAI non disponible.")
            return
        try:
            response = await self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            image_url = response.data[0].url
            embed = discord.Embed(title="🎨 Image Générée", description=f"**Prompt :** {prompt}", color=discord.Color.purple())
            embed.set_image(url=image_url)
            embed.set_footer(text=f"Généré par {interaction.user.display_name}")
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur génération image : {str(e)}")

    # ── COACH ─────────────────────────────────────────────────────────────────
    @app_commands.command(name="coach", description="Obtenir des conseils personnalisés (Coach IA)")
    @app_commands.describe(sujet="Le sujet sur lequel tu veux des conseils")
    async def coach(self, interaction: discord.Interaction, sujet: str):
        await interaction.response.defer()
        prompt = f"Donne-moi 5 conseils pratiques et motivants sur : {sujet}"
        response = await self.get_ai_response(f"coach_{interaction.user.id}", prompt,
            system_prompt="Tu es un coach professionnel bienveillant et motivant. Donne des conseils concrets et applicables.")
        embed = discord.Embed(title="🏆 Coach IA", color=discord.Color.gold())
        embed.add_field(name=f"Conseils sur : {sujet}", value=response[:1024], inline=False)
        await interaction.followup.send(embed=embed)

    # ── ROAST ─────────────────────────────────────────────────────────────────
    @app_commands.command(name="roast", description="Faire rôtir quelqu'un avec l'IA (humour)")
    @app_commands.describe(membre="La personne à rôtir")
    async def roast(self, interaction: discord.Interaction, membre: discord.Member):
        await interaction.response.defer()
        prompt = f"Fais un roast humoristique et bienveillant d'une personne nommée {membre.display_name}. Reste drôle mais pas méchant."
        response = await self.get_ai_response(f"roast_{interaction.user.id}", prompt,
            system_prompt="Tu es un comédien stand-up. Fais des blagues légères et amusantes, jamais blessantes.")
        embed = discord.Embed(title=f"🔥 Roast de {membre.display_name}", color=discord.Color.red())
        embed.description = response[:2000]
        await interaction.followup.send(embed=embed)

    # ── RÉPONSE AUTO ──────────────────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        # Répondre quand le bot est mentionné
        if self.bot.user in message.mentions:
            content = message.content.replace(f"<@{self.bot.user.id}>", "").strip()
            if content:
                async with message.channel.typing():
                    response = await self.get_ai_response(str(message.author.id), content)
                    if len(response) > 2000:
                        response = response[:1997] + "..."
                    await message.reply(response)

async def setup(bot):
    await bot.add_cog(AI(bot))
