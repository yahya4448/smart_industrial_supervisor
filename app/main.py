from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
from datetime import datetime

# Ajouter le répertoire app au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from agents.graph import smart_supervisor, AgentState

app = FastAPI(title="Smart Industrial AI Supervisor", version="1.0.0")

# Ajouter CORS pour que Streamlit puisse communiquer
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variable globale pour stocker l'état actuel par machine
latest_data_by_machine = {
    "M1": {
        "timestamp": None,
        "machine_id": "M1",
        "temperature": 0,
        "vibration": 0,
        "pressure": 0,
        "is_anomaly": False,
        "report": "Aucune donnée reçue"
    },
    "M2": {
        "timestamp": None,
        "machine_id": "M2",
        "temperature": 0,
        "vibration": 0,
        "pressure": 0,
        "is_anomaly": False,
        "report": "Aucune donnée reçue"
    },
    "M3": {
        "timestamp": None,
        "machine_id": "M3",
        "temperature": 0,
        "vibration": 0,
        "pressure": 0,
        "is_anomaly": False,
        "report": "Aucune donnée reçue"
    }
}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Smart Industrial AI Supervisor API!"}

@app.get("/status")
def get_status():
    return {"status": "Running", "version": "1.0.0"}

@app.get("/latest")
def get_latest(machine_id: str = "M1"):
    """
    Retourne les dernières données de capteur et le rapport pour une machine
    """
    return latest_data_by_machine.get(machine_id, latest_data_by_machine["M1"])

@app.post("/ingest")
def ingest_sensor_data(data: dict):
    """
    Reçoit les données IoT et les envoie au workflow multi-agent
    """
    global latest_data_by_machine
    
    try:
        # On crée l'état initial avec les données capteur
        initial_state: dict = {
            "iot_data": data,
            "is_anomaly": False,
            "history": "",
            "manual_rules": "",
            "final_report": ""
        }
        
        # On exécute le workflow
        result = smart_supervisor.invoke(initial_state)
        
        # Déterminer la machine_id
        machine_id = data.get("machine_id", "M1")
        
        # Mettre à jour les dernières données pour cette machine
        latest_data_by_machine[machine_id] = {
            "timestamp": data.get("timestamp", datetime.now().isoformat()),
            "machine_id": machine_id,
            "temperature": data.get("temperature", 0),
            "vibration": data.get("vibration", 0),
            "pressure": data.get("pressure", 0),
            "is_anomaly": result.get("is_anomaly", False),
            "report": result.get("final_report", "")
        }
        
        return {
            "status": "success",
            "report": result.get("final_report", ""),
            "is_anomaly": result.get("is_anomaly", False),
            "machine_id": machine_id
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "machine_id": data.get("machine_id", "Unknown")
        }

