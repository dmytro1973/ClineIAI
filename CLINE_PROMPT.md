# Cline Prompt: MedBook Search AI - Vollständige Webapp

## Projektbeschreibung

**MedBook Search AI** ist eine lokale Pathologie-Literatur-Bibliothek mit KI-Suche. 
Vergleichbar mit Calibre, aber spezialisiert auf medizinische Dokumente.

## Kernfunktionen

### 1. Quellenübergreifende Suche
- AWMF S3-Leitlinien (aktiv, keine Auth)
- WHO Tumour Classification / Blue Books (Auth erforderlich)
- Springer Medizin (Auth erforderlich)
- PubMed (optional Auth)
- CAP Protocols (Auth erforderlich)

### 2. Bibliothek
- Grid/List-Ansicht für PDFs
- Thumbnails automatisch generieren
- Tags und Collections
- Notizen zu Dokumenten
- Volltextsuche in PDFs

### 3. Download Manager
- Queue-basiert mit Prioritäten
- Parallele Downloads (konfigurierbar)
- Resume bei Unterbrechung
- Rate Limiting pro Quelle
- WebSocket für Live-Progress

### 4. Scraper & Wrapper
- BaseScraper für Web-Scraping (Playwright)
- BaseWrapper für APIs
- Konkrete Implementierungen pro Quelle
- Session-Management, Cookies

### 5. Translation (Fly Translate)
- DeepL API
- Claude API
- Medizinisches Glossar
- Export: PDF, DOCX, TXT, MD, HTML

### 6. KI & Search
- Sentence Embeddings (lokales Modell)
- ChromaDB für Vektorsuche
- Claude API für Reranking
- Auto-Tagging von Dokumenten

---

## Technologie-Stack

### Backend (Python)
```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sqlalchemy>=2.0.25
aiosqlite>=0.19.0
pydantic>=2.5.3
pydantic-settings>=2.1.0
pyyaml>=6.0.1
httpx>=0.26.0
aiohttp>=3.9.1
beautifulsoup4>=4.12.2
lxml>=5.1.0
playwright>=1.41.0
pymupdf>=1.23.8
pdfplumber>=0.10.3
pytesseract>=0.3.10
Pillow>=10.2.0
chromadb>=0.4.22
sentence-transformers>=2.2.2
anthropic>=0.14.0
deepl>=1.16.1
cryptography>=41.0.7
tenacity>=8.2.3
```

### Frontend (React + TypeScript)
```
react@18
react-dom@18
react-router-dom@6
typescript@5
vite@5
tailwindcss@3
lucide-react
zustand (State Management)
```

---

## Projektstruktur

```
VerdentMoiApp/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI App
│   │   ├── config.py               # Settings mit Pydantic
│   │   ├── database.py             # SQLAlchemy Setup
│   │   │
│   │   ├── models/                 # SQLAlchemy Models
│   │   │   ├── __init__.py
│   │   │   ├── document.py         # Document, Tag, Collection
│   │   │   ├── download.py         # Download Queue
│   │   │   ├── credential.py       # Encrypted Credentials
│   │   │   └── translation.py      # Translation Cache
│   │   │
│   │   ├── routers/                # API Routes
│   │   │   ├── __init__.py
│   │   │   ├── health.py
│   │   │   ├── search.py
│   │   │   ├── library.py
│   │   │   ├── downloads.py
│   │   │   ├── credentials.py
│   │   │   ├── translation.py
│   │   │   └── settings.py
│   │   │
│   │   ├── scrapers/               # Web Scrapers
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # BaseScraper (abstract)
│   │   │   ├── awmf.py             # AWMF Leitlinien
│   │   │   ├── who.py              # WHO Blue Books
│   │   │   └── springer.py         # Springer Medizin
│   │   │
│   │   ├── wrappers/               # API Wrappers
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # BaseWrapper (abstract)
│   │   │   └── pubmed.py           # PubMed API
│   │   │
│   │   ├── services/               # Business Logic
│   │   │   ├── __init__.py
│   │   │   ├── download_manager.py
│   │   │   ├── indexer.py          # PDF Text Extraction
│   │   │   ├── thumbnail.py        # PDF Thumbnails
│   │   │   ├── embedding.py        # Vector Embeddings
│   │   │   └── translation.py      # Translation Service
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── crypto.py           # Fernet Encryption
│   │       └── rate_limiter.py
│   │
│   ├── requirements.txt
│   └── run.py                      # Startup Script
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── index.css
│   │   │
│   │   ├── components/
│   │   │   ├── Layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── MainLayout.tsx
│   │   │   │
│   │   │   ├── Search/
│   │   │   │   ├── SearchBar.tsx
│   │   │   │   ├── SearchResults.tsx
│   │   │   │   ├── SourceFilter.tsx
│   │   │   │   └── SearchResultCard.tsx
│   │   │   │
│   │   │   ├── Library/
│   │   │   │   ├── LibraryGrid.tsx
│   │   │   │   ├── LibraryList.tsx
│   │   │   │   ├── DocumentCard.tsx
│   │   │   │   ├── DocumentDetails.tsx
│   │   │   │   ├── TagManager.tsx
│   │   │   │   └── CollectionSidebar.tsx
│   │   │   │
│   │   │   ├── Downloads/
│   │   │   │   ├── DownloadQueue.tsx
│   │   │   │   ├── DownloadItem.tsx
│   │   │   │   └── DownloadProgress.tsx
│   │   │   │
│   │   │   ├── Reader/
│   │   │   │   ├── PDFViewer.tsx
│   │   │   │   ├── TranslationPanel.tsx
│   │   │   │   └── NotesPanel.tsx
│   │   │   │
│   │   │   ├── Settings/
│   │   │   │   ├── CredentialsForm.tsx
│   │   │   │   ├── DownloadSettings.tsx
│   │   │   │   ├── TranslationSettings.tsx
│   │   │   │   └── APIKeySettings.tsx
│   │   │   │
│   │   │   └── UI/
│   │   │       ├── Button.tsx
│   │   │       ├── Card.tsx
│   │   │       ├── Input.tsx
│   │   │       ├── Modal.tsx
│   │   │       ├── Spinner.tsx
│   │   │       ├── Alert.tsx
│   │   │       ├── Badge.tsx
│   │   │       ├── Tabs.tsx
│   │   │       └── ProgressBar.tsx
│   │   │
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx       # Übersicht + Quick Search
│   │   │   ├── Search.tsx          # Vollsuche mit Filtern
│   │   │   ├── Library.tsx         # Bibliothek Grid/List
│   │   │   ├── Downloads.tsx       # Download Queue
│   │   │   ├── Reader.tsx          # PDF Viewer + Translation
│   │   │   ├── Settings.tsx        # Alle Einstellungen
│   │   │   └── NotFound.tsx
│   │   │
│   │   ├── stores/
│   │   │   ├── searchStore.ts
│   │   │   ├── libraryStore.ts
│   │   │   ├── downloadStore.ts
│   │   │   └── settingsStore.ts
│   │   │
│   │   ├── services/
│   │   │   ├── api.ts              # API Client
│   │   │   └── websocket.ts        # WebSocket für Downloads
│   │   │
│   │   ├── hooks/
│   │   │   ├── useSearch.ts
│   │   │   ├── useLibrary.ts
│   │   │   └── useDownloads.ts
│   │   │
│   │   ├── types/
│   │   │   ├── search.ts
│   │   │   ├── library.ts
│   │   │   ├── download.ts
│   │   │   └── settings.ts
│   │   │
│   │   └── utils/
│   │       ├── formatters.ts
│   │       └── validators.ts
│   │
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── postcss.config.js
│
├── data/                           # Runtime Data
│   ├── medbook.db                  # SQLite Database
│   ├── chroma/                     # ChromaDB Vectors
│   └── thumbnails/                 # PDF Thumbnails
│
├── library/                        # Downloaded PDFs
│   ├── WHO/
│   ├── S3-Leitlinien/
│   ├── Springer/
│   ├── CAP/
│   ├── PubMed/
│   └── translations/
│
├── config.yaml                     # App Configuration
├── server.js                       # Express Proxy (existiert)
├── package.json                    # Root (existiert)
└── .clinerules                     # Auto-Fix Rules (existiert)
```

---

## API Endpoints

### Health
```
GET  /api/health              # Healthcheck
GET  /api/status              # Detaillierter Status
```

### Search
```
GET  /api/search?q=...&sources=awmf,who&max_results=50
GET  /api/search/sources      # Verfügbare Quellen
GET  /api/search/details?url=...
```

### Library
```
GET    /api/library/documents           # Liste (Filter, Sort, Pagination)
GET    /api/library/documents/{id}      # Einzelnes Dokument
POST   /api/library/documents           # Manuell hinzufügen
DELETE /api/library/documents/{id}
PATCH  /api/library/documents/{id}      # Update (Tags, Notes, etc.)

GET    /api/library/tags
POST   /api/library/tags
DELETE /api/library/tags/{id}

GET    /api/library/collections
POST   /api/library/collections
DELETE /api/library/collections/{id}
```

### Downloads
```
GET    /api/downloads                   # Queue anzeigen
POST   /api/downloads                   # Zur Queue hinzufügen
DELETE /api/downloads/{id}              # Aus Queue entfernen
POST   /api/downloads/{id}/retry        # Erneut versuchen
POST   /api/downloads/pause             # Queue pausieren
POST   /api/downloads/resume            # Queue fortsetzen

WS     /ws/downloads                    # Live Progress Updates
```

### Credentials
```
GET    /api/credentials                 # Liste (ohne Passwörter)
POST   /api/credentials                 # Neue Credentials
DELETE /api/credentials/{source_id}
POST   /api/credentials/validate/{source_id}  # Testen
```

### Translation
```
POST   /api/translation/translate       # Text übersetzen
GET    /api/translation/engines         # Verfügbare Engines
GET    /api/translation/glossary        # Med. Glossar
POST   /api/translation/export          # Als PDF/DOCX exportieren
```

### Settings
```
GET    /api/settings                    # Alle Settings
PATCH  /api/settings                    # Settings updaten
GET    /api/settings/rate-limits
```

---

## Frontend Pages

### Dashboard (/)
- Quick Search Bar
- Letzte Dokumente (Thumbnails)
- Download Status Widget
- Quick Stats (Anzahl Dokumente, etc.)

### Search (/search)
- Große Suchleiste
- Quellenfilter (AWMF, WHO, Springer, PubMed, CAP)
- Ergebnisliste mit:
  - Titel, Autoren, Jahr
  - Quelle-Badge
  - Abstract (klappbar)
  - "Zur Bibliothek" / "Download" Button

### Library (/library)
- Toggle: Grid / List View
- Sidebar: Collections, Tags
- Filter: Quelle, Jahr, Sprache
- Sort: Titel, Datum, Autor
- Dokument-Karten mit Thumbnail

### Downloads (/downloads)
- Aktive Downloads mit Progress
- Warteschlange
- Abgeschlossen / Fehlgeschlagen
- Pause/Resume für Queue

### Reader (/reader/:id)
- PDF Viewer (PDF.js)
- Seitenleiste: Translation Panel
- Seitenleiste: Notes Panel
- Export Button

### Settings (/settings)
- Tabs: Allgemein, Credentials, Downloads, Translation, API Keys
- Credentials für jede Quelle
- API Keys (Claude, DeepL)
- Download-Einstellungen
- Translation-Einstellungen

---

## Implementierungs-Reihenfolge

### Phase 1: Backend Core
1. `backend/app/config.py` - Settings mit Pydantic
2. `backend/app/database.py` - SQLAlchemy async
3. `backend/app/models/` - Alle Models
4. `backend/app/main.py` - FastAPI App
5. `backend/app/routers/health.py`

### Phase 2: Backend Scrapers
1. `backend/app/scrapers/base.py` - BaseScraper
2. `backend/app/scrapers/awmf.py` - AWMF (funktionierend!)
3. `backend/app/routers/search.py`

### Phase 3: Backend Services
1. `backend/app/services/download_manager.py`
2. `backend/app/services/indexer.py`
3. `backend/app/services/thumbnail.py`
4. `backend/app/routers/downloads.py`
5. `backend/app/routers/library.py`

### Phase 4: Frontend Setup
1. Vite + React + TypeScript
2. Tailwind CSS
3. React Router
4. API Client

### Phase 5: Frontend Pages
1. MainLayout + Sidebar
2. Dashboard
3. Search
4. Library
5. Downloads
6. Settings

### Phase 6: Advanced Features
1. Translation Service
2. Embedding Service
3. Reader mit PDF.js
4. WebSocket für Downloads

---

## config.yaml

```yaml
app:
  name: "MedBook Search AI"
  version: "1.1.0"
  host: "127.0.0.1"
  port: 8000
  debug: true

paths:
  data_dir: "./data"
  library_dir: "./library"
  thumbnails_dir: "./data/thumbnails"
  chroma_dir: "./data/chroma"
  database: "./data/medbook.db"

downloads:
  max_parallel: 3
  chunk_size: 1048576
  timeout: 300
  retry_attempts: 3
  retry_delay: 5

indexer:
  ocr_enabled: true
  ocr_language: "deu+eng"
  extract_images: false
  thumbnail_size: [200, 280]

translation:
  default_engine: "deepl"
  default_source_lang: "en"
  default_target_lang: "de"
  cache_enabled: true

ai:
  embedding_model: "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
  reranking_enabled: true
  auto_tagging_enabled: true

rate_limits:
  default: 30
  who: 10
  iarc: 10
  springer: 20
  awmf: 60
  pubmed: 30
  cap: 15
```

---

## Starte mit Phase 1!

1. Erstelle `backend/app/config.py`
2. Erstelle `backend/app/database.py`
3. Erstelle alle Models in `backend/app/models/`
4. Erstelle `backend/app/main.py`
5. Teste mit `python -m uvicorn backend.app.main:app --reload`

Dann weiter zu Phase 2 usw.

**WICHTIG:** Bei AWMF-Scraper erst die tatsächliche Website analysieren, wie die Struktur aufgebaut ist!
