"""Script de lancement du bot avec logging vers fichier."""
import sys, os

# Rediriger stdout/stderr vers un fichier de log
log_file = open("/home/ubuntu/discord_bot/bot_output.log", "w", buffering=1)
sys.stdout = log_file
sys.stderr = log_file

# Lancer le bot
os.chdir("/home/ubuntu/discord_bot")
exec(open("main.py").read())
