# MedBook Search AI

Eine KI-gestützte Literaturverwaltung für Pathologie mit AWMF-Leitlinien und WHO-Klassifikationen.

## Features

- 📚 Dokumentenverwaltung mit Tags und Sammlungen
- 🔍 Volltextsuche in medizinischer Literatur
- 🌐 AWMF-Leitlinien Scraper
- 🤖 KI-Integration für Übersetzungen
- 📥 Download-Manager mit Fortschrittsanzeige

## Tech Stack

- **Backend**: FastAPI + SQLite + SQLAlchemy
- **Frontend**: React + Vite + Tailwind CSS
- **AI**: Claude API Integration

## Deployment

### Railway (Production)
Das Projekt ist für Railway konfiguriert. Push zu GitHub triggert automatisches Deployment.

### Lokal
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 9000

# Frontend
cd frontend
npm install
npm run dev
```

## API Dokumentation

Nach dem Start verfügbar unter: `/docs` (Swagger UI)
