# Le simulateur IoT 
import pandas as pd
import numpy as np
import time
import requests
from datetime import datetime
import random
import sys

API_URL = "http://127.0.0.1:8001/ingest"
TIMEOUT = 5

def generate_sensor_data(machine_id="M1", anomaly=False):
    """Génère une lecture de capteur réaliste selon la machine."""
    
    # Parametres specifiques par machine
    machine_params = {
        "M1": {
            "temp_normal": (75, 2),      # temperature, std_dev
            "temp_anomaly": (110, 5),
            "vib_normal": (10, 1),
            "vib_anomaly": (25, 5),
            "pressure_normal": (30, 2)
        },
        "M2": {
            "temp_normal": (70, 2),
            "temp_anomaly": (100, 5),
            "vib_normal": (12, 2),       # M2: vibration plus importante
            "vib_anomaly": (28, 5),      # M2 sensible aux vibrations
            "pressure_normal": (28, 2)
        },
        "M3": {
            "temp_normal": (72, 2),
            "temp_anomaly": (105, 5),
            "vib_normal": (8, 1),
            "vib_anomaly": (20, 4),
            "pressure_normal": (32, 2)
        }
    }
    
    params = machine_params.get(machine_id, machine_params["M1"])
    
    if anomaly:
        temp = np.random.normal(params["temp_anomaly"][0], params["temp_anomaly"][1])
        vib = np.random.normal(params["vib_anomaly"][0], params["vib_anomaly"][1])
    else:
        temp = np.random.normal(params["temp_normal"][0], params["temp_normal"][1])
        vib = np.random.normal(params["vib_normal"][0], params["vib_normal"][1])
        
    data = {
        "timestamp": datetime.now().isoformat(),
        "machine_id": machine_id,
        "temperature": round(temp, 2),
        "vibration": round(vib, 2),
        "pressure": round(np.random.normal(params["pressure_normal"][0], params["pressure_normal"][1]), 2)
    }
    return data

def send_to_api(data):
    """Envoie les données à l'API FastAPI"""
    try:
        response = requests.post(API_URL, json=data, timeout=TIMEOUT)
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"❌ Erreur API: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        print(f"⚠️  API non disponible sur {API_URL}")
        return None
    except Exception as e:
        print(f"❌ Erreur lors de l'appel API: {str(e)}")
        return None

# Test rapide
if __name__ == "__main__":
    print("=" * 80)
    print("🤖 SIMULATEUR IoT - Smart Industrial Supervisor")
    print(f"📍 Cible API: {API_URL}")
    print("⏸️  Ctrl+C pour arrêter")
    print("=" * 80)
    
    try:
        iteration = 0
        machine_cycle = ["M1", "M2", "M3"]  # Cycle entre les 3 machines
        cycle_index = 0
        
        while True:
            # Choisir la machine selon le cycle
            current_machine = machine_cycle[cycle_index % len(machine_cycle)]
            
            # 1 chance sur 8 de générer une anomalie pour le test
            is_anomaly = np.random.random() > 0.875
            reading = generate_sensor_data(machine_id=current_machine, anomaly=is_anomaly)
            
            print(f"\n[{iteration}] 📊 Machine {current_machine} | T={reading['temperature']}°C, V={reading['vibration']} mm/s, P={reading['pressure']} bar")
            
            if is_anomaly:
                print("⚠️  ANOMALIE INJECTÉE !")
            
            # Envoyer à l'API
            result = send_to_api(reading)
            
            if result:
                print(f"✅ Réponse API: {result['status']}")
                if result['status'] == 'success' and result.get('is_anomaly'):
                    print("🚨 ALERTE DÉTECTÉE PAR LE SYSTÈME")
                    print(f"📋 Rapport:\n{result['report'][:200]}...")
            
            iteration += 1
            cycle_index += 1
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n\n⛔ Simulateur arrêté.")
        sys.exit(0)