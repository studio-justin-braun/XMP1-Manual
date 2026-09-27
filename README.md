# XMP1 Manual

Das vollständige Bedienhandbuch der **MSP-XMP1-Applikation**, aus der ursprünglichen Windows-Hilfedatei `XMP1.HLP` in ein modernes Offline-Handbuch und eine passende PDF-Ausgabe übertragen.

**244 Themen · 125 Abbildungen · 243 Originalverweise · 132 PDF-Seiten**

[HTML-Handbuch](Handbuch/index.html) · [PDF-Handbuch](pdf/XMP1_Handbuch.pdf) · [Prüfbericht](Pruefbericht.md) · [Originalquelle](Quellen/XMP1.HLP)

## Schnellstart

1. Das Repository über **Code → Download ZIP** herunterladen und vollständig entpacken, oder mit Git klonen.
2. `index.html` oder `Handbuch/index.html` im Browser öffnen.
3. Alternativ `pdf/XMP1_Handbuch.pdf` im PDF-Programm öffnen.

Das HTML-Handbuch benötigt **keine Installation, keinen Webserver und keine Internetverbindung**. Texte, Bilder, Formatierung und Suche sind in einer HTML-Datei eingebettet. Der PDF-Link funktioniert, solange die Ordnerstruktur erhalten bleibt.

GitHub zeigt HTML-Dateien in der Codeansicht. Zum Lesen die lokale Datei öffnen oder GitHub Pages wie unten beschrieben aktivieren.

## Funktionen

- Volltextsuche über alle Themen, Überschriften und Originalstichwörter.
- Gemeinsame Suche nach mehreren Wörtern, unabhängig von Groß-/Kleinschreibung und Umlautakzenten.
- Originale Kapitelhierarchie mit ergänzter Abschnittsnummerierung.
- Klickbare Querverweise und 276 Einträge im Stichwortregister.
- Vergrößerbare Originalabbildungen und Navigation für schmale Fenster.
- PDF mit passendem Design, Inhaltsverzeichnis, Lesezeichen und anklickbaren Verweisen.
- Originale BMP- und WMF-Dateien zusätzlich zur browserfähigen PNG-Ausgabe.

**Bedienung:** `Strg + K` öffnet den Suchfokus, `×` setzt die Suche zurück. Ein Klick auf eine Abbildung öffnet die Großansicht. Im PDF wird mit `Strg + F` gesucht. Auf schmalen Bildschirmen öffnet **Inhalt** das Menü einschließlich Suche.

## Inhalt

| Kapitel | Themenbereich |
| --- | --- |
| 1 | Einleitung und Installation |
| 2 | Hauptmaske |
| 3 | XMP1 Konfiguration |
| 4 | XMP1 Bedienung |
| 5 | Soft-ABM-Befehle |
| 6 | Debugging |
| 7 | Planungswerte: Strombedarf und thermische Verlustleistung |

Hierarchie und Reihenfolge sind aus dem Original-Inhaltsverzeichnis rekonstruiert. Alle sichtbaren Quelltexte wurden mit zwei Ausleseverfahren abgeglichen. Die Quelldatei enthält 106 Bitmap- und 19 Vektorgrafiken sowie 17 zusammenhängende Tabellen mit 197 Zeilen und 1.106 Zellen. Separate Audio- oder Videodateien sind nicht enthalten.

## Repository-Aufbau

```text
XMP1-Manual/
├── index.html                 Einstieg für Browser und GitHub Pages
├── Handbuch/
│   ├── index.html             Eigenständiges Offline-Handbuch
│   └── medien/                125 Abbildungen als PNG
├── pdf/                       Fertige PDF-Ausgabe
├── Quellen/
│   ├── XMP1.HLP               Unveränderte Originaldatei
│   ├── inventory.json         Unabhängig extrahierte Themen und Metadaten
│   └── dekompiliert/          RTF, HPJ, PH, Original-BMP und -WMF
├── Pruefung/                  Archivierte Ergebnisse der Ausgabeprüfung
├── scripts/                   Erzeugung, Validierung und Paketierung
├── docs/                      Anleitungen für Build und Veröffentlichung
└── .github/                   Inhaltsprüfung, Pages-Workflow und Vorlagen
```

Neue Builds landen in `build/`, Downloadpakete in `dist/`. Diese Arbeitsverzeichnisse werden nicht in Git aufgenommen.

## GitHub Pages

Der vorbereitete Workflow veröffentlicht die fertige HTML- und PDF-Ausgabe:

1. Das lokale Repository in ein GitHub-Repository übertragen.
2. Unter **Settings → Pages → Build and deployment** als Quelle **GitHub Actions** wählen.
3. Unter **Actions → GitHub Pages → Run workflow** die Veröffentlichung starten.

Die tatsächliche Website-Adresse zeigt anschließend der erfolgreiche Workflow an. Eine konkrete GitHub-Adresse ist hier bewusst nicht vorgegeben, solange kein Remote eingerichtet ist. Details: [GitHub-Veröffentlichung](docs/PUBLISHING.md).

Die automatische **Validierung** läuft bei Pushes und Pull Requests. Eine Pages-Veröffentlichung erfolgt nur durch den manuellen Pages-Workflow.

## Prüfen und neu erstellen

Für die Nutzung der fertigen Handbücher wird Python nicht benötigt. Für die Werkzeuge ist Python 3.12 oder neuer vorgesehen:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/check_repository.py
```

HTML und PDF unter Windows mit installierten Arial-Schriften neu erstellen:

```powershell
.\.venv\Scripts\python.exe scripts/build_manual.py
.\.venv\Scripts\python.exe scripts/verify_manual.py --artifact-root build
```

Nur die HTML-Ausgabe lässt sich plattformübergreifend mit `--html-only` erstellen. Die vollständigen Schritte, die Quelle der ursprünglichen Extraktion und der Umgang mit WMF-Grafiken stehen in [BUILD.md](docs/BUILD.md).

Ein geprüftes ZIP-Paket der im Repository enthaltenen Ausgabe erzeugt:

```powershell
.\.venv\Scripts\python.exe scripts/package_manual.py
```

## Quellenstand und Grenzen

Die Dokumentation bewahrt den historischen Stand der Quelldatei. Technische Angaben, alte Systemanforderungen und Bedienabläufe wurden nicht auf heutige Systeme umgeschrieben. Screenshots behalten ihre ursprüngliche Auflösung. Die Suche durchsucht die Hilfetexte und Stichwörter; Bildbeschriftungen wurden nicht zusätzlich per OCR erfasst.

Die SHA-256-Prüfsumme der Originaldatei lautet:

```text
487089c8f0aab8dafafb1712b284400b90cec0411c963d2c4fbcf455cb6849f6
```

Einzelheiten zur Konvertierung und Prüfung: [Prüfbericht](Pruefbericht.md). Änderungen an dieser Ausgabe: [Changelog](CHANGELOG.md).

## Mitwirken und Quellenhinweise

Fehler lassen sich über die vorbereitete Issue-Vorlage melden. Hinweise für Änderungen stehen in [CONTRIBUTING.md](CONTRIBUTING.md).

Originalvermerk aus der Hilfedatei: **® PET2BK**. Für die historischen Inhalte wird durch dieses Repository keine neue Lizenz erteilt. Quellen, verwendete Werkzeuge und die Abgrenzung der Rechte sind in [NOTICE.md](NOTICE.md) dokumentiert.
