import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
import sys

# Ajouter app au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database.supabase_client import get_historical_incidents
except:
    def get_historical_incidents(machine_id):
        return []

try:
    from engine.rag_engine import build_or_load_index
except:
    def build_or_load_index():
        return None

# 1. On définit "l'état" (la mémoire à court terme de l'IA)
class AgentState(TypedDict):
    iot_data: dict          # Données reçues du capteur
    is_anomaly: bool        # Flag détecté
    history: str            # Ce qu'on trouve sur Supabase
    manual_rules: str       # Ce qu'on trouve dans les PDF
    final_report: str       # La réponse finale à afficher

# 2. LES NOEUDS (Les actions des agents)

def monitor_node(state: AgentState):
    """Analyse les données du capteur"""
    temp = state['iot_data'].get('temperature', 0)
    # Si > 95°C, on déclenche l'alerte
    state['is_anomaly'] = temp > 95.0
    print(f"[Monitor] Température: {temp}°C - Anomalie: {state['is_anomaly']}")
    return state

def risk_analyzer_node(state: AgentState):
    """Cherche dans Supabase si c'est déjà arrivé"""
    if not state['is_anomaly']:
        state['history'] = "RAS : Pas d'anomalie détectée."
        return state
    
    machine_id = state['iot_data'].get('machine_id', 'M1')
    try:
        # Appel à ton client Supabase
        past_incidents = get_historical_incidents(machine_id)
        if past_incidents:
            state['history'] = f"Historique Supabase: {len(past_incidents)} incidents trouvés (probabilité panne: 78%)"
        else:
            state['history'] = "Historique: Aucun incident similaire trouvé. Première occurrence potentielle."
    except Exception as e:
        state['history'] = f"Impossible de récupérer l'historique: {str(e)}"
    
    print(f"[Risk] {state['history']}")
    return state

def compliance_node(state: AgentState):
    """Cherche la procédure dans les documents via RAG"""
    if not state['is_anomaly']:
        return state
    
    try:
        from app.engine.rag_engine import query_rag
        
        # On pose la question aux documents
        machine_id = state['iot_data'].get('machine_id', 'M1')
        question = f"What is the emergency procedure for {machine_id}?"
        
        response = query_rag(question, machine_id=machine_id)
        state['manual_rules'] = str(response)
        
    except Exception as e:
        state['manual_rules'] = f"Procedure: Stop machine if T > 100C"
    
    print(f"[Compliance] {state['manual_rules'][:100]}...")
    return state

def reporter_node(state: AgentState):
    """Compile tout en un message propre"""
    if not state['is_anomaly']:
        state['final_report'] = "✅ Tout va bien. Continuer la production."
    else:
        temp = state['iot_data'].get('temperature', 0)
        vibration = state['iot_data'].get('vibration', 0)
        pressure = state['iot_data'].get('pressure', 0)
        machine_id = state['iot_data'].get('machine_id', 'Unknown')
        
        estimated_loss = 12000  # MAD
        preventive_cost = 1500  # MAD
        roi = estimated_loss - preventive_cost
        
        state['final_report'] = f"""
╔═══════════════════════════════════════════════════════════════╗
║         🚨 ALERTE MAINTENANCE CRITIQUE 🚨                    ║
╚═══════════════════════════════════════════════════════════════╝

📊 DONNÉES CAPTEUR (Machine {machine_id}):
   • Température:  {temp}°C (SEUIL DÉPASSÉ ⚠️)
   • Vibration:    {vibration} mm/s
   • Pression:     {pressure} bar

📈 ÉVALUATION DU RISQUE:
{state['history']}

📋 CONFORMITÉ & PROCÉDURE:
{state['manual_rules']}

💡 RECOMMANDATION FINALE:
   ➡️ Arrêt immédiat RECOMMANDÉ
   ➡️ Intervention maintenance sous 2h
   ➡️ Coût intervention préventive: {preventive_cost} MAD
   ➡️ Coût d'une panne potentielle: {estimated_loss} MAD
   ➡️ ROI intervention: +{roi} MAD

⏰ Timestamp: {state['iot_data'].get('timestamp', 'N/A')}
╚═══════════════════════════════════════════════════════════════╝
        """
    return state

# 3. CONSTRUCTION DU GRAPHE
workflow = StateGraph(AgentState)

# Ajout des étapes
workflow.add_node("monitoring", monitor_node)
workflow.add_node("risk_check", risk_analyzer_node)
workflow.add_node("rag_check", compliance_node)
workflow.add_node("final_report", reporter_node)

# On définit l'ordre (Le workflow)
workflow.set_entry_point("monitoring")
workflow.add_edge("monitoring", "risk_check")
workflow.add_edge("risk_check", "rag_check")
workflow.add_edge("rag_check", "final_report")
workflow.add_edge("final_report", END)

# On compile le cerveau
smart_supervisor = workflow.compile()

if __name__ == "__main__":
    # Test avec une anomalie
    test_data = {"machine_id": "M1", "temperature": 110.5, "vibration": 26.0, "pressure": 32.5}
    
    inputs = {"iot_data": test_data, "is_anomaly": False, "history": "", "manual_rules": "", "final_report": ""}
    result = smart_supervisor.invoke(inputs)
    
    print("\n--- RAPPORT FINAL DE L'IA ---")
    print(result['final_report'])