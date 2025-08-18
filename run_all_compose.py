import os
import subprocess

# Chemin racine à partir duquel chercher les fichiers docker-compose
racine = os.getcwd()  # ou remplace par un chemin absolu, ex : "/home/user/projects"

# Noms possibles des fichiers docker-compose
fichiers_compose = ["docker-compose.yaml","docker-compose.yml"]

def lancer_docker_compose(chemin):
    print(f"\n➡️  Dossier : {chemin}")
    try:
        subprocess.run(["docker-compose", "up", "-d"], cwd=chemin, check=True)
        print("✅ docker-compose up -d lancé avec succès.")
    except subprocess.CalledProcessError:
        print("❌ Erreur lors de l'exécution de docker-compose.")

# Parcours des sous-dossiers
for dossier_racine, sous_dossiers, fichiers in os.walk(racine):
    for fichier in fichiers:
        if fichier in fichiers_compose:
            lancer_docker_compose(dossier_racine)
            break  # éviter de lancer plusieurs fois si plusieurs fichiers sont présents