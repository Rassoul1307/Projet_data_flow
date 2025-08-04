import os
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine, text
import sys
import time
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration de la base de données MySQL
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'appuser'),
    'password': os.getenv('DB_PASSWORD', 'apppassword123'),
    'database': os.getenv('DB_NAME', 'meteo_db'),
    'port': int(os.getenv('DB_PORT', '3306'))
}

def attendre_mysql(max_tentatives=60, delai=3):
    """
    Attendre que MySQL soit prêt avec gestion d'erreurs améliorée
    """
    logger.info(" Attente que MySQL soit prêt...")
    
    for tentative in range(max_tentatives):
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            connection.close()
            logger.info("MySQL est prêt!")
            return True
            
        except mysql.connector.Error as e:
            if tentative < max_tentatives - 1:
                logger.info(f" Tentative {tentative + 1}/{max_tentatives} - {str(e)[:100]}")
                time.sleep(delai)
            else:
                logger.error(f"Connexion MySQL échouée après {max_tentatives} tentatives")
                
        except Exception as e:
            logger.error(f"Erreur inattendue: {str(e)}")
            time.sleep(delai)
    
    return False

def creer_table_meteo():
    """
    Crée la table avec gestion des données manquantes et index optimisés
    """
    logger.info("Création de la table weather_data...")
    
    requete_creation = """
    CREATE TABLE IF NOT EXISTS weather_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        date DATE NOT NULL,
        temp_max DECIMAL(5,2) NULL,
        temp_min DECIMAL(5,2) NULL, 
        precipitations_mm DECIMAL(6,2) NULL DEFAULT 0,
        wind_kmh DECIMAL(5,2) NULL,
        humidity_percent DECIMAL(5,2) NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        
        -- Index pour optimiser les requêtes
        INDEX idx_date (date),
        INDEX idx_temp (temp_max, temp_min),
        
        -- Contrainte unique sur la date pour éviter les doublons
        UNIQUE KEY unique_date (date)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute(requete_creation)
        connection.commit()
        cursor.close()
        connection.close()
        
        logger.info("Table weather_data créée avec succès!")
        return True
        
    except mysql.connector.Error as erreur:
        logger.error(f"Erreur lors de la création de la table: {erreur}")
        return False

def nettoyer_donnees(donnees):
    """
    Nettoie et valide les données avant import
    """
    logger.info("Nettoyage des données...")
    
    # Statistiques initiales
    lignes_initiales = len(donnees)
    logger.info(f"Données initiales: {lignes_initiales} lignes")
    
    # Convertir la colonne date en datetime
    try:
        donnees['date'] = pd.to_datetime(donnees['date'])
    except Exception as e:
        logger.error(f"Erreur conversion des dates: {e}")
        return None
    
    # Supprimer les lignes où TOUTES les valeurs météo sont manquantes
    colonnes_meteo = ['temp_max', 'temp_min', 'precipitations_mm', 'wind_kmh', 'humidity_percent']
    donnees_propres = donnees.dropna(subset=['date'])  # Date obligatoire
    
    # Identifier les lignes avec toutes les données météo manquantes
    lignes_vides = donnees_propres[colonnes_meteo].isna().all(axis=1)
    donnees_propres = donnees_propres[~lignes_vides]
    
    # Remplacer les valeurs manquantes par NULL (pandas NaN)
    # MySQL gérera les NULL correctement
    
    # Validation des données
    lignes_finales = len(donnees_propres)
    lignes_supprimees = lignes_initiales - lignes_finales
    
    if lignes_supprimees > 0:
        logger.info(f"{lignes_supprimees} lignes supprimées (vides ou dates invalides)")
    
    # Statistiques des données manquantes par colonne
    for col in colonnes_meteo:
        manquantes = donnees_propres[col].isna().sum()
        if manquantes > 0:
            logger.info(f"{col}: {manquantes} valeurs manquantes")
    
    return donnees_propres

def lire_fichier_csv():
    """
    Lit et traite le fichier CSV avec gestion des erreurs améliorée
    """
    chemin_csv = "/app/data/weather_data.csv"
    logger.info(f"Lecture du fichier CSV: {chemin_csv}")
    
    try:
        if not os.path.exists(chemin_csv):
            logger.error(f"Fichier CSV non trouvé: {chemin_csv}")
            logger.info("Assure-toi que ton fichier CSV est dans le dossier data/")
            return None
        
        # Lecture avec gestion des erreurs d'encodage
        try:
            donnees = pd.read_csv(chemin_csv, encoding='utf-8')
        except UnicodeDecodeError:
            logger.info("Tentative avec encodage latin-1...")
            donnees = pd.read_csv(chemin_csv, encoding='latin-1')
        
        logger.info(f"Fichier lu avec succès!")
        logger.info(f"   - Lignes: {len(donnees)}")
        logger.info(f"   - Colonnes: {list(donnees.columns)}")
        
        # Nettoyage des données
        donnees_propres = nettoyer_donnees(donnees)
        
        return donnees_propres
        
    except Exception as erreur:
        logger.error(f"Erreur lors de la lecture du CSV: {erreur}")
        return None

def importer_vers_mysql(donnees):
    """
    Importe les données avec gestion des doublons et des erreurs
    """
    logger.info("Import des données vers MySQL...")
    
    try:
        # Connexion SQLAlchemy
        engine = create_engine(
            f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}",
            echo=False  # Mettre à True pour debug SQL
        )
        
        # Vérifier les données existantes pour éviter les doublons
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) as count FROM weather_data"))
            count_existant = result.fetchone()[0]
            
        if count_existant > 0:
            logger.info(f"{count_existant} enregistrements déjà présents")
            
            # Option 1: Remplacer les données existantes
            choix_import = 'replace'  # ou 'append' pour ajouter
            logger.info(f"Mode d'import: {choix_import}")
        else:
            choix_import = 'append'
        
        # Import des données
        lignes_importees = donnees.to_sql(
            name='weather_data',
            con=engine,
            if_exists=choix_import,
            index=False,
            method='multi'  # Import par batch pour de meilleures performances
        )
        
        # Vérification post-import
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) as count FROM weather_data"))
            total_final = result.fetchone()[0]
            
        logger.info(f"Import terminé!")
        logger.info(f"   - Lignes traitées: {len(donnees)}")
        logger.info(f"   - Total en base: {total_final}")
        
        return True
        
    except Exception as erreur:
        logger.error(f"Erreur lors de l'import: {erreur}")
        # Afficher plus de détails sur l'erreur
        import traceback
        logger.error(f"Détails: {traceback.format_exc()}")
        return False

def afficher_statistiques():
    """
    Affiche des statistiques sur les données importées
    """
    try:
        engine = create_engine(
            f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        )
        
        with engine.connect() as conn:
            # Statistiques générales
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_records,
                    MIN(date) as date_debut,
                    MAX(date) as date_fin,
                    AVG(temp_max) as temp_max_moyenne,
                    AVG(temp_min) as temp_min_moyenne,
                    AVG(precipitations_mm) as precipitations_moyenne
                FROM weather_data
            """))
            
            stats = result.fetchone()
            if stats:
                logger.info(" Statistiques des données importées:")
                logger.info(f"   - Total d'enregistrements: {stats[0]}")
                logger.info(f"   - Période: {stats[1]} à {stats[2]}")
                logger.info(f"   - Température max moyenne: {stats[3]:.1f}°C")
                logger.info(f"   - Température min moyenne: {stats[4]:.1f}°C")
                logger.info(f"   - Précipitations moyennes: {stats[5]:.1f}mm")
                
    except Exception as e:
        logger.warning(f"Impossible d'afficher les statistiques: {e}")

def main():
    """
    Fonction principale avec gestion d'erreurs complète
    """
    logger.info("Démarrage de l'import des données météo")
    logger.info("=" * 60)
    
    try:
        # Étape 1: Attendre MySQL
        if not attendre_mysql():
            logger.error("Impossible de se connecter à MySQL")
            sys.exit(1)
        
        # Étape 2: Créer la table
        if not creer_table_meteo():
            logger.error("Échec de la création de la table")
            sys.exit(1)
        
        # Étape 3: Lire le CSV
        donnees = lire_fichier_csv()
        if donnees is None or donnees.empty:
            logger.error("Aucune donnée à importer")
            sys.exit(1)
        
        # Étape 4: Importer
        if not importer_vers_mysql(donnees):
            logger.error("Échec de l'import")
            sys.exit(1)
        
        # Étape 5: Statistiques
        afficher_statistiques()
        
        logger.info("=" * 60)
        logger.info("Import terminé avec succès!")
        logger.info("Connexion MySQL disponible sur:")
        logger.info("   - Host: localhost:3307")
        logger.info("   - User: appuser")
        logger.info("   - Password: apppassword123")
        logger.info("   - Database: meteo_db")
        
    except KeyboardInterrupt:
        logger.info("Import interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
        import traceback
        logger.error(f"Détails: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()