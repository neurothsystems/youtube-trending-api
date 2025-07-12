# 🎯 YouTube Trending Analyzer

**Finde die echten Trending-Videos auf YouTube - nicht nur die mit den meisten Views!**

## Was macht dieses Projekt?

Dieses Programm sucht auf YouTube nach Videos und findet heraus, welche **wirklich** im Trend liegen. 

**Der Unterschied:** YouTube zeigt oft nur Videos mit vielen Views. Unser Programm ist schlauer und berücksichtigt auch:
- Wie viele Kommentare ein Video hat
- Wie neu das Video ist  
- Wie aktiv die Zuschauer sind

## Wie funktioniert es?

1. **Du gibst ein Suchwort ein** (z.B. "Künstliche Intelligenz")
2. **Das Programm sucht Videos** der letzten Tage
3. **Es berechnet einen "Trending-Score"** für jedes Video
4. **Du bekommst die echten Trending-Videos** angezeigt

## Was brauchst du zum Starten?

### Für die einfache Nutzung:
- Einen Computer mit Internet
- Einen YouTube API-Schlüssel (kostenlos von Google)

### Für Entwickler:
- Python 3.9 oder neuer
- Docker (optional, aber empfohlen)

## Schnellstart - So startest du das Programm:

### Option 1: Mit Docker (einfacher)
```bash
# 1. Dieses Projekt herunterladen
git clone https://github.com/DEIN-USERNAME/youtube-trending-api.git
cd youtube-trending-api

# 2. Deine Konfiguration erstellen
cp config.ini.example.ini config.ini
# Öffne config.ini und trage deinen YouTube API-Schlüssel ein

# 3. Programm starten
docker-compose up

# 4. Im Browser öffnen: http://localhost:8000
```

### Option 2: Direkt mit Python
```bash
# 1. Dieses Projekt herunterladen
git clone https://github.com/DEIN-USERNAME/youtube-trending-api.git
cd youtube-trending-api

# 2. Benötigte Pakete installieren
pip install -r minimal_requirements.txt

# 3. Konfiguration erstellen
cp config.ini.example.ini config.ini
# Öffne config.ini und trage deinen YouTube API-Schlüssel ein

# 4. Programm starten
python simple_server.py

# 5. Im Browser öffnen: http://localhost:8000
```

## Wie bekomme ich einen YouTube API-Schlüssel?

1. Gehe zu [Google Cloud Console](https://console.cloud.google.com/)
2. Erstelle ein neues Projekt (oder wähle ein vorhandenes)
3. Aktiviere die "YouTube Data API v3"
4. Erstelle einen API-Schlüssel
5. Kopiere den Schlüssel in deine `config.ini` Datei

**Keine Sorge:** Google gibt dir 10.000 kostenlose Anfragen pro Tag - das reicht für die meisten Projekte!

## Was kann das Programm?

### Webseite (http://localhost:8000):
- Übersichtliche Startseite mit allen Funktionen
- Tests um zu prüfen ob alles funktioniert
- Einfache Bedienung im Browser

### API-Funktionen:
- **GET /test** - Prüft ob das Programm läuft
- **GET /config-test** - Prüft deinen API-Schlüssel  
- **GET /youtube-test** - Testet die Verbindung zu YouTube
- **GET /analyze** - Findet Trending-Videos

### Beispiel-Suchen:
- `http://localhost:8000/analyze?query=künstliche intelligenz`
- `http://localhost:8000/analyze?query=musik 2024&days=7&top_count=10`

## Wie funktioniert der Trending-Algorithmus?

**Einfach erklärt:**
```
Trending-Score = (Views + Kommentare × 10) / (Alter in Stunden ^ 1.3) × (1 + Engagement-Rate)
```

**Was bedeutet das?**
- Videos mit vielen **Kommentaren** bekommen Bonus-Punkte
- **Neuere Videos** werden bevorzugt  
- Videos mit hoher **Interaktion** steigen höher
- **Bessere Ergebnisse** als nur nach Views zu sortieren

## Projektstruktur

```
youtube-trending-api/
├── simple_server.py          # Das Hauptprogramm
├── Dockerfile                # Für Docker-Container
├── docker-compose.yml        # Für lokale Entwicklung  
├── minimal_requirements.txt   # Benötigte Python-Pakete
├── config.ini.example.ini    # Vorlage für Einstellungen
└── README.md                 # Diese Datei
```

## Häufige Probleme und Lösungen

### "Fehler: API-Schlüssel nicht gefunden"
- Prüfe ob die Datei `config.ini` existiert
- Prüfe ob dein API-Schlüssel korrekt eingetragen ist
- Stelle sicher, dass der Schlüssel keine Leerzeichen enthält

### "Fehler: YouTube API-Verbindung fehlgeschlagen"
- Prüfe deine Internetverbindung
- Prüfe ob dein API-Schlüssel noch gültig ist
- Prüfe ob du das tägliche Limit überschritten hast

### "Programm startet nicht"
- Prüfe ob Python 3.9+ installiert ist: `python --version`
- Installiere die Pakete: `pip install -r minimal_requirements.txt`
- Prüfe ob Port 8000 frei ist

## Deployment (Das Programm online stellen)

Du kannst dein Programm kostenlos online stellen mit:

- **Railway.app** (empfohlen)
- **Heroku** 
- **Google Cloud Run**
- **AWS**

**Anleitung für Railway:**
1. Konto bei railway.app erstellen
2. "Deploy from GitHub" wählen
3. Dieses Repository auswählen
4. Environment Variable `YOUTUBE_API_KEY` setzen
5. Deployment starten

## Entwicklung und Erweiterungen

### Geplante Features:
- 🎨 Schönere Webseite mit modernem Design
- 📊 Diagramme und Statistiken
- 💾 Videos als Favoriten speichern
- 🔄 Automatische Updates alle paar Minuten
- 📱 Mobile App

### Mithelfen:
Du willst mitentwickeln? Super!
1. "Fork" dieses Repository
2. Mache deine Änderungen
3. Sende einen "Pull Request"

## Lizenz

Dieses Projekt ist Open Source und kostenlos nutzbar (MIT Lizenz).

## Kontakt und Support

- **Probleme melden:** [GitHub Issues](https://github.com/DEIN-USERNAME/youtube-trending-api/issues)
- **Fragen stellen:** [GitHub Discussions](https://github.com/DEIN-USERNAME/youtube-trending-api/discussions)

---

⭐ **Hat dir das Projekt geholfen? Dann gib uns einen Stern auf GitHub!**

**Entwickelt mit ❤️ für bessere YouTube-Trends**
