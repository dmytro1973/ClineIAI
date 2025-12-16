# KI-API Integration - Einrichtungshandbuch

## Echte API-Integration aktivieren

Die Anwendung unterstützt jetzt echte API-Integration für OpenAI und Anthropic (Claude). Hier ist eine Anleitung, wie Sie die echte API-Integration einrichten:

## Voraussetzungen

1. **API-Schlüssel besorgen**:
   - OpenAI API-Schlüssel: [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)
   - Anthropic API-Schlüssel: [https://console.anthropic.com/account/keys](https://console.anthropic.com/account/keys)

2. **Abhängigkeiten installieren**:
```bash
pip install requests python-dotenv
```

## Einrichtung

### 1. Umgebungsvariable setzen

Erstellen Sie eine `.env`-Datei im Hauptverzeichnis des Backend-Projekts:

```bash
cd backend
touch .env
```

Fügen Sie Ihren API-Schlüssel zur `.env`-Datei hinzu:

```env
OPENAI_API_KEY=Ihr_API_Schlüssel_hier
```

### 2. API-Auswahl

Die Anwendung unterstützt automatisch beide API-Typen:
- **OpenAI-Modelle**: gpt-4, gpt-3.5-turbo, etc.
- **Anthropic-Modelle**: claude-3, claude-2, etc.

Die richtige API wird automatisch basierend auf dem ausgewählten Modell gewählt.

### 3. Anwendung starten

Starten Sie das Backend mit der echten API-Integration:

```bash
cd backend
uvicorn app.main:app --reload
```

## Unterstützte Modelle

### OpenAI Modelle:
- `gpt-4`
- `gpt-4-turbo`
- `gpt-3.5-turbo`

### Anthropic (Claude) Modelle:
- `claude-3-opus`
- `claude-3-sonnet`
- `claude-3-haiku`
- `claude-2`

## Fehlerbehandlung

Die Anwendung implementiert eine robuste Fehlerbehandlung:
1. **Automatischer Fallback**: Bei API-Fehlern wird automatisch auf Mock-Antworten zurückgegriffen
2. **Fehlerprotokollierung**: API-Fehler werden in der Konsole protokolliert
3. **Benutzerfeedback**: Klare Fehlermeldungen werden an den Benutzer zurückgegeben

## Testen der Integration

1. **Chat-Funktion testen**:
   - Navigieren Sie zur Chat-Seite
   - Wählen Sie ein Modell aus (z.B. "gpt-4" oder "claude-3")
   - Stellen Sie eine Frage und überprüfen Sie, ob Sie eine echte API-Antwort erhalten

2. **Dokumentenanalyse testen**:
   - Gehen Sie zur Dokumente-Seite
   - Analysieren Sie ein Dokument
   - Die Analyse sollte jetzt mit der echten KI durchgeführt werden

## Wichtige Hinweise

1. **API-Kosten**: Beachten Sie die Kosten der API-Nutzung
2. **Rate Limits**: Achten Sie auf die API-Rate-Limits
3. **Sicherheit**: Bewahren Sie Ihren API-Schlüssel sicher auf und geben Sie ihn nicht weiter
4. **Mock-Modus**: Wenn kein API-Schlüssel vorhanden ist, wird automatisch der Mock-Modus verwendet

## Fehlerbehebung

**Problem**: API-Aufrufe schlagen fehl
- **Lösung**: Überprüfen Sie, ob Ihr API-Schlüssel gültig ist
- **Lösung**: Überprüfen Sie Ihr API-Guthaben
- **Lösung**: Überprüfen Sie Ihre Internetverbindung

**Problem**: Falsche API-Antworten
- **Lösung**: Überprüfen Sie, ob Sie das richtige Modell ausgewählt haben
- **Lösung**: Überprüfen Sie die API-Dokumentation für das ausgewählte Modell

## Unterstützung

Bei weiteren Fragen oder Problemen mit der API-Integration können Sie:
1. Die offizielle API-Dokumentation konsultieren
2. Die Fehlermeldungen in der Konsole überprüfen
3. Den Mock-Modus für Tests ohne API-Schlüssel verwenden

Viel Erfolg mit der echten KI-Integration!
