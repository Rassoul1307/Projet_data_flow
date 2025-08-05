from bs4 import BeautifulSoup
import json
import logging
import time
import calendar
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Configuration du logging
logging.basicConfig(
    filename="meteo.log", 
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode='w'  # Écrase le fichier à chaque exécution
)

def nettoyer_valeur_numerique(valeur):
    """Nettoie et convertit une valeur en nombre"""
    if not valeur or valeur.strip() == '':
        return None
    
    # Remplacer la virgule par un point pour la conversion française
    valeur_nettoyee = valeur.strip().replace(',', '.')
    
    try:
        return float(valeur_nettoyee)
    except ValueError:
        return None


def extraire_donnees_jour(soup, annee, mois, jour):
    """Extrait les données météo d'un jour spécifique"""
    
    try:
        # Extraction selon la structure HTML fournie
        temp_max_elem = soup.find('span', id='max-temp')
        pluie_elem = soup.find('div', id='bubble-rain')
        vent_elem = soup.find('div', id='bubble-wind')
        humidite_elem = soup.find('div', id='bubble-humidity')
        
        # Nettoyage et conversion des données
        temp_max = nettoyer_valeur_numerique(temp_max_elem.text) if temp_max_elem else None
        precipitation = nettoyer_valeur_numerique(pluie_elem.text) if pluie_elem else None
        vent = nettoyer_valeur_numerique(vent_elem.text) if vent_elem else None
        humidite = nettoyer_valeur_numerique(humidite_elem.text) if humidite_elem else None
        
        # Détermination de la saison (supprimée - plus utilisée)
        
        data = {
            "ville": "Dakar",
            "pays": "Sénégal",
            "date": f"{annee}-{mois:02d}-{jour:02d}",
            "année": annee,
            "mois": mois,
            "jour": jour,
            "température_max_celsius": temp_max,
            "précipitations_mm": precipitation,
            "vent_kmh": vent,
            "humidité_pourcentage": int(humidite) if humidite else None,
            "timestamp_extraction": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return data
        
    except Exception as e:
        logging.error(f"Erreur extraction données : {e}")
        return None

def main():
    # Configuration du navigateur
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=options)
    
    # Liste des mois à scraper 
    mois_liste = list(range(1, 8))  # Janvier à juillet
    
    # Tous les jours du mois
    jours_echantillon = list(range(1, 32))
    
    resultats = []
    annee = 2025
    
    try:
        compteur = 0
        
        logging.info(f" Début du scraping pour l'année {annee}")
        
        for mois in mois_liste:
            # Obtenir le nombre de jours dans le mois
            _, nb_jours_mois = calendar.monthrange(annee, mois)
            
            logging.info(f"Début scraping mois {mois} ({calendar.month_name[mois]}) - {nb_jours_mois} jours")
            
            for jour in jours_echantillon:
                # Vérifier que le jour existe dans ce mois
                if jour > nb_jours_mois:
                    continue
                    
                compteur += 1
                
                try:
                    url = f"https://www.meteoart.com/africa/senegal/dakar?page=past-weather#day={jour}&month={mois}"
                    logging.info(f"[{compteur}] Scraping {jour:02d}/{mois:02d}/{annee}")
                    
                    driver.get(url)
                    
                    # Attendre le chargement des éléments météo
                    try:
                        WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.ID, 'max-temp'))
                        )
                        # Attendre un peu plus pour que les animations se terminent
                        time.sleep(2)
                    except TimeoutException:
                        logging.warning(f"Timeout pour {jour}/{mois}/{annee}")
                        continue
                    
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    
                    # Extraire les données
                    data = extraire_donnees_jour(soup, annee, mois, jour)
                    
                    if data and data.get('température_max_celsius') is not None:
                        resultats.append(data)
                        
                        
                        logging.info(f"Données extraites : T°{data['température_max_celsius']}° - Pluie:{data['précipitations_mm']}mm")
                    else:
                        logging.warning(f" Aucune donnée valide pour {jour}/{mois}/{annee}")
                    
                    # Pause entre requêtes pour éviter la surcharge
                    time.sleep(1)
                    
                except Exception as e:
                    logging.error(f"Erreur pour {jour}/{mois}/{annee} : {e}")
                    continue
            
            logging.info(f"Mois {mois} terminé ({calendar.month_name[mois]}) - {len([r for r in resultats if r['mois'] == mois])} jours extraits")
    
    finally:
        driver.quit()
    
    # Sauvegarde des résultats
    if resultats:
        # Sauvegarde dans un seul fichier JSON
        with open("meteo_dakar_annuelle_by_SDiarra.json", "w", encoding="utf-8") as f:
            json.dump(resultats, f, ensure_ascii=False, indent=2)
        
        print(f"Scraping terminé avec succès !")
        print(f"meteo_dakar_annuelle_by_SDiarra.json")
        
    else:
        logging.warning("Aucune donnée extraite")
        print("Aucune donnée n'a pu être extraite")

if __name__ == "__main__":
    main()


