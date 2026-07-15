import json
import random

def generate_bots():
    # Liste de base pour inspiration
    prefixes = ["Super", "Ultra", "Mega", "Cyber", "Dark", "Light", "Pro", "Smart", "Easy", "Fast", "Safe", "Guard", "Music", "Fun", "Game", "Eco", "Level", "Mod", "Admin", "Helper", "Social", "Community", "Global", "Space", "Void", "Star", "Moon", "Sun", "Fire", "Water", "Ice", "Thunder", "Nature", "Animal", "Bot", "Robot", "Droid", "Nexus", "Core", "Prime"]
    suffixes = ["Bot", "Master", "Helper", "Guard", "Pro", "Plus", "Premium", "Elite", "Nexus", "Core", "Node", "Hub", "System", "Manager", "Tools", "Box", "Lab", "Studio", "Cloud", "Net", "Link", "Sync", "Flow", "Wave", "Pulse", "Zen", "Dash", "X", "Z", "One"]
    categories = ["Modération", "Musique", "Économie", "Jeux", "Fun", "Utilitaires", "IA", "Protection", "Niveaux", "Giveaway", "Tickets", "Images", "Statistiques"]
    
    # Commandes disponibles dans le bot (liste exhaustive)
    all_commands = [
        "ban", "kick", "mute", "unmute", "warn", "warnings", "clearwarns", "clear", "slowmode", "lock", "unlock", "nick", "role", "userinfo", "serverinfo",
        "automod", "addword", "removeword", "automodstatus",
        "ticketpanel", "addticket", "removeticket", "tickets",
        "balance", "daily", "work", "deposit", "withdraw", "pay", "leaderboard", "gamble", "rank", "levelboard",
        "gstart", "greroll", "gend",
        "play", "pause", "resume", "skip", "stop", "leave", "queue", "volume", "nowplaying", "loop",
        "8ball", "coinflip", "rps", "hug", "pat", "slap", "quote", "owo", "water", "tree", "setcounting", "dice", "poll", "avatar", "invites",
        "ask", "resetai", "translate", "summarize", "correct", "imagine", "coach", "roast",
        "backup", "backuplist", "backupload", "backupdelete",
        "setup", "setwelcome", "setlogs", "setverify", "verify",
        "nuke", "autorole", "bump", "addemoji", "listemojis", "stats", "reactionrole", "ping", "help", "announce", "embed", "say",
        "transform", "reset", "botlist"
    ]

    # Bots réels déjà présents avec leurs commandes principales
    existing_bots = {
        "mee6": {"name": "MEE6", "avatar": "https://cdn.discordapp.com/avatars/159985870458322944/b50adff099924dd5e6b72d13b3b5e4ad.png", "status": "Modération & Niveaux | /help", "description": "🤖 MEE6 — Modération, niveaux XP, musique.", "color": 0xFF0000, "active_commands": ["ban", "kick", "mute", "warn", "rank", "leaderboard", "play", "help", "transform", "reset", "botlist"]},
        "dyno": {"name": "Dyno", "avatar": "https://cdn.discordapp.com/avatars/161660517914509312/b3c4a5f8b7e4c3d2a1f0e9d8c7b6a5f4.png", "status": "Modération Premium | /help", "description": "⚙️ Dyno — Modération premium et automod.", "color": 0x4A90D9, "active_commands": ["ban", "mute", "warn", "clear", "automod", "announce", "help", "transform", "reset", "botlist"]},
        "carlbot": {"name": "Carl-bot", "avatar": "https://cdn.discordapp.com/avatars/235148962103951360/dfbdd87f3e426e2e4a3f8f8e8e8e8e8e.png", "status": "Automod & Logs | /help", "description": "🔴 Carl-bot — Automod avancé et rôles.", "color": 0xE74C3C, "active_commands": ["automod", "reactionrole", "warn", "clear", "embed", "help", "transform", "reset", "botlist"]},
        "probot": {"name": "ProBot", "avatar": "https://cdn.discordapp.com/avatars/282859044593598464/a_f3e3e3e3e3e3e3e3e3e3e3e3e3e3e3.png", "status": "Protection & Modération | /help", "description": "🛡️ ProBot — Modération et protection.", "color": 0x2ECC71, "active_commands": ["ban", "kick", "warn", "automod", "setwelcome", "help", "transform", "reset", "botlist"]},
        "yagpdb": {"name": "YAGPDB.xyz", "avatar": "https://cdn.discordapp.com/avatars/204255221017214977/a_e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3.png", "status": "Yet Another General Purpose Bot", "description": "🟠 YAGPDB — Bot polyvalent et automod.", "color": 0xE67E22, "active_commands": ["automod", "role", "warn", "clear", "stats", "help", "transform", "reset", "botlist"]},
        "wick": {"name": "Wick", "avatar": "https://cdn.discordapp.com/avatars/536991182035746816/a_e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3.png", "status": "Anti-Nuke | /help", "description": "🔒 Wick — Protection avancée anti-nuke.", "color": 0x2C3E50, "active_commands": ["automod", "automodstatus", "ban", "kick", "help", "transform", "reset", "botlist"]},
        "clyde": {"name": "Clyde", "avatar": "https://cdn.discordapp.com/avatars/1081004946872352958/a_e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3.png", "status": "IA Discord | /ask", "description": "🤖 Clyde — L'assistant IA officiel.", "color": 0x5865F2, "active_commands": ["ask", "translate", "summarize", "correct", "coach", "roast", "help", "transform", "reset", "botlist"]},
        "dankmemer": {"name": "Dank Memer", "avatar": "https://cdn.discordapp.com/avatars/270904126974590976/a_e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3.png", "status": "Mèmes & Économie | /help", "description": "😂 Dank Memer — Mèmes et économie.", "color": 0xF1C40F, "active_commands": ["balance", "daily", "work", "gamble", "pay", "coinflip", "help", "transform", "reset", "botlist"]},
        "owo": {"name": "OwO", "avatar": "https://cdn.discordapp.com/avatars/408785106942164992/a_e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3.png", "status": "OwO | /help", "description": "🐾 OwO — Chasse et animaux kawaii.", "color": 0xFF69B4, "active_commands": ["owo", "hug", "pat", "slap", "balance", "daily", "help", "transform", "reset", "botlist"]},
        "fredboat": {"name": "FredBoat", "avatar": "https://cdn.discordapp.com/avatars/221516296939839488/a_e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3.png", "status": "Musique | /play", "description": "🎵 FredBoat — Bot musical gratuit.", "color": 0x1ABC9C, "active_commands": ["play", "pause", "resume", "skip", "stop", "leave", "queue", "volume", "nowplaying", "loop", "help", "transform", "reset", "botlist"]},
        "xenon": {"name": "Xenon Bot", "avatar": "https://cdn.discordapp.com/avatars/567703512763334685/a_e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3.png", "status": "Backup | /backup", "description": "📦 Xenon — Sauvegarde de serveurs.", "color": 0x3498DB, "active_commands": ["backup", "backuplist", "backupload", "backupdelete", "help", "transform", "reset", "botlist"]},
    }

    bots = existing_bots.copy()
    
    # Générer jusqu'à 1000
    while len(bots) < 1000:
        p = random.choice(prefixes)
        s = random.choice(suffixes)
        name = f"{p}{s}"
        key = name.lower()
        
        if key in bots:
            name = f"{p} {s} {random.randint(1, 999)}"
            key = name.lower().replace(" ", "")
            
        cat = random.choice(categories)
        color = random.randint(0, 0xFFFFFF)
        
        # Sélectionner un sous-ensemble aléatoire de commandes pour le bot fictif
        num_commands = random.randint(3, 10) # Entre 3 et 10 commandes aléatoires
        active_cmds = random.sample(all_commands, num_commands)
        # Assurer que les commandes de base sont toujours là
        active_cmds.extend([cmd for cmd in ["help", "transform", "reset", "botlist"] if cmd not in active_cmds])
        
        bots[key] = {
            "name": name,
            "avatar": f"https://cdn.discordapp.com/embed/avatars/{random.randint(0, 5)}.png",
            "status": f"{cat} | /help",
            "description": f"✨ **{name}** — Le meilleur bot de {cat.lower()} pour ton serveur !",
            "color": color,
            "commands_hint": f"Utilise `/help` pour voir les commandes de {name}.",
            "active_commands": active_cmds
        }
        
    return bots

if __name__ == "__main__":
    all_bots = generate_bots()
    with open("data/bots_database.json", "w", encoding="utf-8") as f:
        json.dump(all_bots, f, indent=2, ensure_ascii=False)
    print(f"✅ Base de données de {len(all_bots)} bots générée !")
