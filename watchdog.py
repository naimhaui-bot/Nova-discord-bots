import subprocess
import time
import sys
import os

# Configuration
BOT_SCRIPT = "main.py"
LOG_FILE = "bot_persistence.log"
RESTART_DELAY = 5  # Secondes avant redémarrage

def log(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def run_bot():
    while True:
        log("Démarrage du bot...")
        try:
            # On lance le bot et on attend qu'il s'arrête
            process = subprocess.Popen(
                [sys.executable, "-u", BOT_SCRIPT],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Lecture des logs en temps réel pour le debug
            with open("bot_output.log", "w") as out:
                for line in process.stdout:
                    out.write(line)
                    out.flush()
                    if "✅ Bot prêt !" in line:
                        log("Le bot est en ligne et prêt.")
            
            process.wait()
            exit_code = process.returncode
            log(f"Le bot s'est arrêté avec le code : {exit_code}")
            
        except Exception as e:
            log(f"Erreur fatale dans le watchdog : {e}")
        
        log(f"Redémarrage dans {RESTART_DELAY} secondes...")
        time.sleep(RESTART_DELAY)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    log("Lancement du système de surveillance 24/7")
    run_bot()
