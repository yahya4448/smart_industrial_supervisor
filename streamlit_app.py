import streamlit as st
import requests
from datetime import datetime
import time

# Configuration
st.set_page_config(
    page_title="Smart Industrial AI Supervisor",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
    .alert { background-color: #ffebee; padding: 15px; border-radius: 5px; margin: 10px 0; color: #d32f2f; font-weight: bold; }
    .success { background-color: #e8f5e9; padding: 15px; border-radius: 5px; margin: 10px 0; color: #388e3c; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Smart Industrial AI Supervisor")
st.markdown("### Système Multi-Agent pour la Maintenance Prédictive Industrie 4.0")

# Sidebar
with st.sidebar:
    st.markdown("⚙️ **Configuration**")
    api_url = st.text_input("API URL", "http://127.0.0.1:8001", key="api_url_input")
    
    st.markdown("📊 **Sélection Machine**")
    machine_id = st.selectbox("Machine", ["M1", "M2", "M3"])
    
    st.markdown("---")
    st.markdown("**Taux Rafraîchissement**")
    refresh_rate = st.slider("Secondes", 2, 10, 3)

# Session state
if 'latest_data' not in st.session_state:
    st.session_state.latest_data = None

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📋 Alertes", "🧪 Tests", "ℹ️ À propos"])

# ============= FONCTION POUR RÉCUPÉRER LES DERNIÈRES DONNÉES =============
def get_latest_data(machine_id="M1"):
    """Récupère les dernières données de l'API pour une machine spécifique"""
    try:
        response = requests.get(f"{api_url}/latest?machine_id={machine_id}", timeout=2)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

# ============= TAB 1: DASHBOARD =============
with tab1:
    st.subheader("📊 État du système EN TEMPS RÉEL")
    st.write(f"**Machine sélectionnée:** {machine_id}")
    
    # Placeholder pour forcer le rafraîchissement
    metric_placeholder = st.empty()
    status_placeholder = st.empty()
    time_placeholder = st.empty()
    
    # Récupérer les données pour la machine sélectionnée
    latest = get_latest_data(machine_id)
    
    if latest:
        # Afficher les métriques
        with metric_placeholder.container():
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="🌡️ Température",
                    value=f"{latest.get('temperature', 0):.1f}°C",
                    delta=f"{latest.get('temperature', 0) - 75:.1f}°C"
                )
            
            with col2:
                st.metric(
                    label="📈 Vibration",
                    value=f"{latest.get('vibration', 0):.1f} mm/s",
                    delta=f"{latest.get('vibration', 0) - 10:.1f} mm/s"
                )
            
            with col3:
                st.metric(
                    label="💨 Pression",
                    value=f"{latest.get('pressure', 0):.1f} bar",
                    delta=f"{latest.get('pressure', 0) - 30:.1f} bar"
                )
        
        # Afficher le statut
        with status_placeholder.container():
            st.write("")
            if latest.get('is_anomaly'):
                st.markdown('<div class="alert">🚨 ANOMALIE DÉTECTÉE - Intervention requise</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="success">✅ Système Normal - Production continue</div>', unsafe_allow_html=True)
        
        # Timestamp
        with time_placeholder.container():
            st.caption(f"⏰ Dernière mise à jour: {latest.get('timestamp', 'N/A')}")
    else:
        with metric_placeholder.container():
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="🌡️ Température", value="--°C")
            with col2:
                st.metric(label="📈 Vibration", value="-- mm/s")
            with col3:
                st.metric(label="💨 Pression", value="-- bar")
        
        with status_placeholder.container():
            st.warning("⚠️ Aucune donnée disponible. Assurez-vous que le simulateur IoT est en cours d'exécution.")
    
    # Boutons de contrôle
    st.write("")
    col_info, col_refresh = st.columns(2)
    with col_info:
        st.info(f"✅ API: {api_url}")
    with col_refresh:
        if st.button("🔄 Rafraîchir maintenant"):
            st.rerun()

# ============= TAB 2: ALERTES =============
with tab2:
    st.subheader("📋 Journal des Alertes")
    st.write(f"**Machine sélectionnée:** {machine_id}")
    
    # Récupérer les dernières données pour afficher l'alerte si présente
    latest = get_latest_data(machine_id)
    
    if latest and latest.get('is_anomaly'):
        st.markdown(latest.get('report', 'N/A'))
    else:
        st.info("✅ Aucune alerte active - Système en conditions normales")

# ============= TAB 3: TESTS =============
with tab3:
    st.subheader("🧪 Tester le Workflow Multi-Agent")
    
    st.markdown("**Scénario 1: Données NORMALES**")
    if st.button("📊 Envoyer Test Normal (T=76°C)"):
        with st.spinner("Envoi..."):
            data = {
                "machine_id": machine_id,
                "temperature": 76.5,
                "vibration": 10.2,
                "pressure": 30.1
            }
            try:
                response = requests.post(f"{api_url}/ingest", json=data, timeout=5)
                result = response.json()
                
                if result.get('is_anomaly'):
                    st.markdown('<div class="alert">🚨 Anomalie détectée</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="success">✅ Système Normal</div>', unsafe_allow_html=True)
                
                st.text_area("Rapport", value=result.get('report', 'N/A'), height=150)
                
            except Exception as e:
                st.error(f"❌ Erreur: {e}")
    
    st.markdown("---")
    st.markdown("**Scénario 2: Données ANORMALES (Surchauffe)**")
    if st.button("🔥 Envoyer Test Anomalie (T=115°C)"):
        with st.spinner("Envoi..."):
            data = {
                "machine_id": machine_id,
                "temperature": 115.5,
                "vibration": 25.2,
                "pressure": 35.8,
                "timestamp": datetime.now().isoformat()
            }
            try:
                response = requests.post(f"{api_url}/ingest", json=data, timeout=5)
                result = response.json()
                
                if result.get('is_anomaly'):
                    st.markdown('<div class="alert">🚨 **ANOMALIE CRITIQUE DÉTECTÉE**</div>', unsafe_allow_html=True)
                
                st.text_area("Rapport Détaillé", value=result.get('report', 'N/A'), height=300)
                
            except Exception as e:
                st.error(f"❌ Erreur: {e}")

# ============= TAB 4: ABOUT =============
with tab4:
    st.markdown("""
    ## 📘 À propos du Projet
    
    **Smart Industrial AI Supervisor** est un MVP (Minimum Viable Product) pour la maintenance prédictive Industrie 4.0.
    
    ### 🎯 Qu'est-ce que ça fait ?
    
    **Regarde les machines usine EN DIRECT** et dit **"ATTENTION ça va casser!"** AVANT que ça casse.
    
    Les machines genèrent 3 types de données:
    - 🌡️ **Température** (normal: 70-80°C, alerte si >95°C)
    - 📈 **Vibration** (normal: 8-12 mm/s, alerte si >20 mm/s)
    - 💨 **Pression** (normal: 28-32 bar)
    
    ### 🤖 Les 4 Agents Intelligents
    
    **1️⃣ Data Monitoring Agent**
    - Lit les données capteurs
    - Détecte anomalies statistiques
    - Seuil: Température > 95°C → ⚠️ ALERTE
    
    **2️⃣ Risk Detection Agent**
    - Cherche dans Supabase: "Est-ce que j'ai déjà eu ce problème?"
    - Calcule: Probabilité de panne = 78%
    - Historique incidents: 3 pannes similaires trouvées
    
    **3️⃣ Compliance Agent (RAG)**
    - Interroge les PDFs (procédures, normes ISO)
    - Trouve: "Norme exige arrêt si T > 100°C"
    - Vérifie conformité règlementaire
    
    **4️⃣ Decision Agent**
    - Compile tout en rapport final
    - Recommandation: **Arrêt immédiat**
    - Calcul ROI: 
      - Intervention préventive: 1500 MAD
      - Panne potentielle: 12000 MAD
      - **ROI: +10500 MAD**
    
    ### 📊 Structure Supabase
    
    **Table: `incidents`**
    ```
    ├─ id (PRIMARY KEY)
    ├─ machine_id (text) → "M1", "M2", "M3"
    ├─ description (text) → "Surchauffe détectée", "Vibration anormale"
    ├─ severity (number) → 0-100
    └─ timestamp (datetime)
    ```
    
    **Exemple:**
    | id | machine_id | description | severity | timestamp |
    |----|-----------|-------------|----------|-----------|
    | 1 | M1 | Surchauffe 115°C | 95 | 2026-03-14 15:50 |
    | 2 | M1 | Vibration 28 mm/s | 87 | 2026-03-10 14:30 |
    | 3 | M1 | Pression anormale | 65 | 2026-03-08 09:15 |
    
    Quand tu envoies (T=115°C), l'agent Risk cherche dans Supabase:
    ```
    SELECT * FROM incidents 
    WHERE machine_id = 'M1' 
    ORDER BY timestamp DESC
    ```
    Résultat: **3 incidents trouvés → Probabilité panne: 78%**
    
    ### 📊 Ce que tu dois créer dans Supabase
    
    1. Aller à https://supabase.com
    2. Créer table **incidents**
    3. Ajouter colonnes:
       - id (auto-increment)
       - machine_id (text)
       - description (text)
       - severity (number)
       - timestamp (timestamp)
    4. Ajouter quelques données de test (voir tableau ci-dessus)
    
    ### 🔌 Comment les données circulent
    
    ```
    Simulateur IoT (tourne en boucle)
    │
    ├─→ Génère random: T=76°C, V=10mm/s, P=30bar
    │   (ou T=115°C si anomalie)
    │
    └─→ Envoie via POST http://127.0.0.1:8001/ingest
       │
       └─→ FastAPI reçoit → Exécute les 4 agents
           │
           ├─→ Monitor: T > 95? NON
           ├─→ Risk: Check Supabase → "3 incidents trouvés"
           ├─→ Compliance: Check PDFs → "Procédure trouvée"
           └─→ Decision: Génère rapport → Stocke dans latest_data
    
    Dashboard (rafraîchit toutes les 3 secondes)
    │
    └─→ GET http://127.0.0.1:8001/latest
        │
        └─→ Affiche: Température, Vibration, Pression, Status
    ```
    
    ### 🛠️ Stack Technologique
    
    | Composant | Technologie |
    |-----------|-------------|
    | Backend | FastAPI |
    | Orchestration | LangGraph (4 agents) |
    | RAG | LlamaIndex + Groq |
    | Vecteurs | FAISS + HuggingFace |
    | Base données | Supabase PostgreSQL |
    | Frontend | Streamlit |
    | Simulation | Python |
    """)

st.sidebar.markdown("---")
st.sidebar.markdown("*Industrie 4.0 | IA Multi-Agent | Maintenance Prédictive*")

# Auto-refresh
placeholder = st.empty()
with placeholder.container():
    time.sleep(refresh_rate)
    st.rerun()



