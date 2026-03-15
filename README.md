# 🤖 Smart Industrial AI Supervisor

> **Industrie 4.0 Maintenance Prediction System** using Multi-Agent AI Architecture

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95%2B-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Latest-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 What is This?

A **real-time predictive maintenance system** for industrial machines that:
- 🔍 **Monitors** 3 production machines simultaneously
- 🚨 **Detects** anomalies using intelligent agents
- 📚 **Retrieves** emergency procedures from PDF documents via RAG
- 💰 **Calculates** ROI for preventive interventions
- 📊 **Displays** live metrics on an interactive dashboard

**Perfect for**: Manufacturing facilities, IoT deployments, Industry 4.0 projects

---

## ✨ Key Features

### 🤖 Multi-Agent Orchestration
- **4 Specialized Agents** working in sequence
  1. 📊 **Monitor Agent** - Detects temperature anomalies
  2. 📈 **Risk Analyzer** - Queries incident history from Supabase
  3. 📋 **Compliance Agent** - Extracts procedures from PDF documents
  4. 📝 **Reporter Agent** - Compiles detailed reports with ROI calculations

### 📚 Smart RAG System
- Reads machine-specific procedures from **PDF documents**
- Keyword-based search with fallback to general standards
- Priority: `procedure_M{id}.pdf` > `iso_standards.pdf`

### 🌐 Real-Time Dashboard
- 3 production machines (M1, M2, M3)
- Live metrics: Temperature, Vibration, Pressure
- Auto-refresh every 3 seconds
- Machine selector for quick switching

### 🗄️ Multi-Source Integration
- **Supabase PostgreSQL** - Incident history database
- **FastAPI** - REST API with OpenAPI docs
- **Streamlit** - Interactive web dashboard
- **IoT Simulator** - Realistic sensor data generation

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Pip (package manager)

### Installation (5 minutes)

```bash
# Clone repository
git clone <repository-url>
cd smart_industrial_supervisor

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your Supabase credentials
```

### Launch System (3 Terminals)

**Terminal 1 - Backend API:**
```bash
python -m uvicorn app.main:app --port 8001 --reload
```
→ FastAPI running on http://127.0.0.1:8001

**Terminal 2 - Dashboard:**
```bash
streamlit run streamlit_app.py --server.port 8501
```
→ Streamlit running on http://localhost:8501

**Terminal 3 - IoT Simulator:**
```bash
python scripts/sensor_sim.py
```
→ Generates realistic sensor data every 3 seconds

### 🌐 Access Points

| Service | URL |
|---------|-----|
| **Dashboard** | http://localhost:8501 |
| **API Swagger** | http://127.0.0.1:8001/docs |
| **API ReDoc** | http://127.0.0.1:8001/redoc |

---

## 📋 System Architecture

```
┌─────────────────┐
│  IoT Simulator  │  → Generates T°C, Vibration, Pressure
└────────┬────────┘
         │ POST /ingest
         ▼
┌─────────────────────────────────────┐
│     FastAPI Backend (Port 8001)     │
│  ┌───────────────────────────────┐  │
│  │  LangGraph Workflow (4 Agents)│  │
│  │  1. Monitor                   │  │
│  │  2. Risk Analyzer (Supabase)  │  │
│  │  3. Compliance (RAG PDFs)     │  │
│  │  4. Reporter (ROI calc)       │  │
│  └───────────────────────────────┘  │
└────────┬─────────────────┬──────────┘
         │                 │
    Data Storage    /latest endpoint
         │                 │
         ▼                 ▼
    ┌─────────────┐    ┌──────────────┐
    │  Supabase   │    │   Streamlit  │
    │  Database   │    │   Dashboard  │
    └─────────────┘    └──────────────┘
                             │
                           Browser
                    http://localhost:8501
```

---

## 📊 Usage Examples

### Via Dashboard (Recommended)
1. Open http://localhost:8501
2. Select machine from sidebar (M1, M2, M3)
3. View live metrics
4. Click "Alerts" tab to see full reports
5. Use "Tests" tab to manually trigger scenarios

### Via API (Swagger)
1. Open http://127.0.0.1:8001/docs
2. Click on POST `/ingest`
3. Enter test data:
```json
{
  "machine_id": "M1",
  "temperature": 115.5,
  "vibration": 25.2,
  "pressure": 35.8
}
```
4. Click "Execute"
5. View response with procedure and ROI

### Via Command Line
```bash
curl -X POST http://127.0.0.1:8001/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "M1",
    "temperature": 115.5,
    "vibration": 25.2,
    "pressure": 35.8
  }'
```

---

## 📁 Project Structure

```
smart_industrial_supervisor/
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── agents/
│   │   └── graph.py            # LangGraph workflow
│   ├── database/
│   │   ├── model.py            # Data structures
│   │   └── supabase_client.py   # Database client
│   └── engine/
│       └── rag_engine.py        # RAG with PDFs
├── data/
│   └── documents/
│       ├── iso_standards.pdf    # ISO norms
│       ├── procedure_M1.pdf     # M1 procedures
│       ├── procedure_M2.pdf     # M2 procedures
│       └── procedure_M3.pdf     # M3 procedures
├── scripts/
│   ├── sensor_sim.py            # IoT simulator
│   └── convert_to_pdf.py        # TXT→PDF converter
├── streamlit_app.py             # Dashboard UI
├── requirements.txt             # Dependencies
├── .gitignore                   # Git exclusions
└── README.md                    # This file
```

---

## 🔌 API Endpoints

### Core Endpoints

**GET `/status`**
- Returns: API health status
```json
{"status": "Running", "version": "1.0.0"}
```

**GET `/latest`** (Query: `?machine_id=M1`)
- Returns: Latest data for specified machine
```json
{
  "timestamp": "2024-03-15T12:34:56",
  "machine_id": "M1",
  "temperature": 75.2,
  "vibration": 10.5,
  "pressure": 30.1,
  "is_anomaly": false,
  "report": "✅ Système Normal"
}
```

**POST `/ingest`**
- Input: Sensor readings
- Returns: Anomaly detection + AI-generated report
```json
{
  "status": "success",
  "is_anomaly": false,
  "machine_id": "M1",
  "report": "Detailed analysis..."
}
```

### Documentation
- **Swagger UI**: http://127.0.0.1:8001/docs
- **ReDoc**: http://127.0.0.1:8001/redoc

---

## 🧪 Testing

### Run Integration Tests
```bash
python test_pdf_workflow.py
```

Expected output:
```
✅ M1 (115°C) → Procédure PDF M1 chargée
✅ M2 (105°C, 28mm/s) → Procédure PDF M2 chargée
✅ M3 (105°C) → Procédure PDF M3 chargée
```

### Manual Testing Scenarios
1. **Normal Operation**: Temperature ~75°C → ✅ Normal
2. **M1 Overheating**: Temperature ~115°C → 🚨 Alert M1 procedure
3. **M2 Vibration**: Vibration ~28 mm/s → 🚨 Alert M2 procedure
4. **M3 High Temp**: Temperature ~105°C → 🚨 Alert M3 procedure

---

## 📚 Technologies Used

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend | FastAPI | REST API & orchestration |
| Agents | LangGraph | Multi-agent workflow |
| Search | PyPDF | PDF document extraction |
| Frontend | Streamlit | Interactive dashboard |
| Database | Supabase | Incident history |
| Simulation | NumPy | Realistic sensor data |
| Docs | ReportLab | PDF generation |

---

## 🔐 Environment Variables

Create `.env` file with:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Optional: Groq LLM for future extensions
GROQ_API_KEY=your-groq-key
```

---

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing-feature`)
5. Open Pull Request


## 🐛 Troubleshooting

### FastAPI won't start
```bash
# Check if port 8001 is in use
netstat -ano | findstr :8001
# Kill process if needed
taskkill /PID <pid> /F
```

### Streamlit connection error
- Ensure FastAPI is running on port 8001
- Check CORS settings in `app/main.py`
- Verify API URL in Streamlit sidebar

### PDF procedures not loading
```bash
# Test RAG directly
python -c "from app.engine.rag_engine import query_rag; print(query_rag('procedure', 'M1'))"
```

### Supabase connection issues
- Verify `.env` contains correct credentials
- Check Supabase project is active
- Ensure `incidents` table exists

---

## 📞 Support

- 📧 Email: medyahyakachi@gmail.com
---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🏆 Project Status

| Component | Status |
|-----------|--------|
| Core API | ✅ Production Ready |
| Dashboard | ✅ Fully Functional |
| RAG System | ✅ PDF-based |
| Multi-Agent | ✅ 4 Agents Working |
| Testing | ✅ Integrated Tests |

**Last Updated**: March 15, 2026

---

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangGraph Guide](https://github.com/langchain-ai/langgraph)
- [Streamlit Tutorial](https://docs.streamlit.io/)
- [Supabase Docs](https://supabase.com/docs)

---

**Made with ❤️ for Industrial AI**
