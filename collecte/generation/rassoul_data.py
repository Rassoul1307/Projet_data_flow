import random
from datetime import datetime, timedelta
import json


def generate_weather_data(start_date, num_days):
    weather_data = []
    current_date = start_date

    with open("./data/generation/rassoul_data_meteo.json", "w", encoding="utf-8") as file:

        for _ in range(num_days):
            data = {
                    "ville": "Dakar",
                    "longitude": 14.693425,
                    "latitude": -17.447938,
                    "Date": current_date.strftime("%d/%m/%Y %H:%M:%S"),
                    "température": f"{random.randint(10, 30)} °C",
                    "humidité": f"{random.randint(40, 80)} %",
                    "couverture_nuages": f"{random.randint(0,80)} %",
                    "intensite_pluies": f"{random.randint(0,70)} mm/h",
                    "vitesse_vent": f"{random.randint(0,20)} km/h",
                }
            
            # Écrire chaque objet JSON sur une ligne séparée
            file.write(json.dumps(data, ensure_ascii=False) + "\n")

            weather_data.append(data)
            current_date -= timedelta(minutes=15)

       

        #print(weather_data)

    return weather_data

start_date = datetime.now()


generate_weather_data(start_date, 1000)
#save_to_json(generate_weather_data(start_date, 100), "./data/weather_data.json")


