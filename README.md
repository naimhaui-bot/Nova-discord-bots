# 🤖 Bot Discord Ultra-Complet

Ce bot regroupe les fonctionnalités de plus de **50 bots Discord populaires** : MEE6, Dyno, Carl-bot, Wick, Xenon, Dank Memer, OwO, Tickety, FredBoat, Clyde, Probot, Security Bot, et bien d'autres.

## 🌟 Fonctionnalités

- **🛡️ Modération :** Ban, kick, mute, warn, clear, lock, slowmode, etc.
- **🚨 AutoMod & Anti-Raid :** Protection contre le spam, les raids, les liens, et l'anti-nuke ultra-rapide (comme Security Bot).
- **🎫 Tickets :** Système de support avec panel, transcription et fermeture.
- **💰 Économie & Niveaux :** Monnaie, daily, work, banque, gamble, leaderboard, XP et niveaux.
- **🎉 Giveaways :** Création, participation via boutons, reroll et fin anticipée.
- **🎵 Musique :** Lecture YouTube, file d'attente, pause, volume, boucle.
- **🤖 Intelligence Artificielle :** Chat IA (comme Clyde), génération d'images (Midjourney-like), traduction, résumé.
- **📦 Backup (Xenon) :** Sauvegarde et restauration complète de la structure du serveur.
- **⚙️ Setup Serveur :** Création automatique d'une structure de serveur professionnelle.
- **💥 Commandes Spéciales :** Nuke secret (`#Nuke#`), statistiques serveur, emojis, autorole, etc.

## 🚀 Installation

### 1. Prérequis
- Python 3.10 ou supérieur
- FFmpeg (pour la musique)
- Un token de bot Discord
- Une clé API OpenAI (optionnelle, pour l'IA)

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Configurer le bot
Créez un fichier `.env` ou définissez les variables d'environnement suivantes :
```bash
export DISCORD_TOKEN="votre_token_discord"
export OPENAI_API_KEY="votre_cle_api_openai" # Optionnel
```

### 4. Lancer le bot
```bash
python main.py
```

## 🛠️ Utilisation
Toutes les commandes utilisent le système de **Slash Commands (/)**. Tapez `/help` dans votre serveur pour voir la liste complète.

### 🔒 La commande secrète Nuke
Comme demandé, le bot possède une commande secrète de Nuke.
Si un utilisateur possédant au moins un rôle (autre que @everyone) envoie exactement le message `#Nuke#`, le bot supprimera tous les salons et les recréera avec le nom `⭐│nuke` contenant exactement 19 étoiles (⭐).
