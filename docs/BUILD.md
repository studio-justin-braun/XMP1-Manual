# Handbuch bauen und prüfen

Die fertige Ausgabe in `Handbuch/` und `pdf/` kann ohne Entwicklungswerkzeuge benutzt werden. Die Skripte dienen der nachvollziehbaren Weiterentwicklung.

## Umgebung einrichten

Für HTML, Validierung und Paketierung: Python 3.12 oder neuer. Für den vollständigen PDF-Neubau: Windows mit `C:/Windows/Fonts/arial.ttf`, `arialbd.ttf`, `ariali.ttf` und `arialbi.ttf`.

Im Repository-Ordner unter PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Wenn `py -3.12` nicht verfügbar ist, kann `python -m venv .venv` mit einer passenden Python-Version verwendet werden. Unter Linux/macOS lautet der Interpreter nach `python3 -m venv .venv` entsprechend `.venv/bin/python`.

## Vorhandene Ausgabe prüfen

```powershell
.\.venv\Scripts\python.exe scripts/check_repository.py
.\.venv\Scripts\python.exe scripts/verify_manual.py
```

Die erste Prüfung kontrolliert die Quellprüfsumme, Reihenfolge und Texte der Themen, Linkziele, Tabellenzellen, Suchdaten, eingebettete Bilder, PDF und lokale Dokumentationslinks. Die zweite prüft zusätzlich alle PDF-Textabsätze und Seitenbegrenzungen und rendert die Seiten zur visuellen Kontrolle nach `build/qa/`.

Ein erfolgreicher automatischer Lauf ersetzt nicht die Sichtprüfung von geänderten Seiten, Tabellen oder Bildern. Die vorhandenen Browserprotokolle in `Pruefung/` sind archivierte Ergebnisse der ursprünglichen Ausgabeprüfung.

## Neu erstellen

HTML und PDF:

```powershell
.\.venv\Scripts\python.exe scripts/build_manual.py
.\.venv\Scripts\python.exe scripts/verify_manual.py --artifact-root build
```

Nur HTML, auch ohne Windows-Schriften:

```powershell
.\.venv\Scripts\python.exe scripts/build_manual.py --html-only
```

Ergebnisse:

- `build/Handbuch/index.html` und `build/Handbuch/medien/`
- `build/pdf/XMP1_Handbuch.pdf` beim vollständigen Build
- `build/qa/model.json` mit rekonstruiertem Themenbaum und Textvergleich

Der Build überschreibt die ausgelieferte Ausgabe im Repository nicht. Erst nach der Prüfung die gewünschten Dateien aus `build/` nach `Handbuch/` bzw. `pdf/` übernehmen. Bei einem reinen HTML-Build ist der PDF-Link im Build-Ordner erst nutzbar, nachdem dort auch die PDF-Ausgabe liegt.

`scripts/manual.css` und `scripts/manual.js` werden in die HTML-Ausgabe eingebettet. Inhalte, Tabellen, Abschnittshierarchie und PDF-Satz entstehen durch `scripts/build_manual.py`. Das Editionsdatum ist im Generator ausdrücklich gesetzt; es bezeichnet die dokumentierte Ausgabe, nicht jeden erneuten Build.

## Bildkonvertierung

Die bereits vorhandenen PNGs werden beim Handbuch-Build verwendet. Für eine erneute Umwandlung der Original-BMP/WMF unter Windows:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/convert_images.ps1
```

Die Ergebnisse stehen in `build/medien/`. BMP wird verlustfrei in PNG gespeichert, WMF über Windows GDI+ mit 300 dpi gerendert. Neu konvertierte Bilder visuell prüfen und bei Bedarf nach `Handbuch/medien/` übernehmen, bevor das Handbuch neu gebaut wird. Die Originalmedien bleiben in `Quellen/dekompiliert/`.

## Herkunft der Ausgangsdaten

Der normale Build benötigt keinen WinHelp-Viewer und führt die HLP-Datei nicht aus. Er arbeitet mit den archivierten Dekompilierungsdaten und einem unabhängigen Textinventar:

- `Quellen/dekompiliert/XMP1.RTF`: vollständige Texte, Linkziele, Formate, Bildmarker und Tabellengeometrie aus HelpDeco.
- `Quellen/inventory.json`: Themen, Quelltexte, Suchstichwörter und Metadaten aus winhlp 0.4.1.
- `Quellen/XMP1.HLP`: unveränderte Binärquelle mit festgehaltener SHA-256-Prüfsumme.

Die einmalige Gewinnung dieser Ausgangsdaten und die damaligen Konvertierungsprobleme sind im [Prüfbericht](../Pruefbericht.md) beschrieben. Die alten Decompiler-Binärdateien werden nicht im Repository verteilt. Das Repository enthält bewusst die bereits gewonnenen Originaldaten, sodass ein regulärer Neubau ohne Download dieser Werkzeuge möglich ist.

## Downloadpaket und Website

```powershell
.\.venv\Scripts\python.exe scripts/package_manual.py
.\.venv\Scripts\python.exe scripts/prepare_site.py
```

Das ZIP liegt unter `dist/`. Der Pages-Ordner `build/site/` enthält nur den Browser-Einstieg, `Handbuch/` und `pdf/`. Die relativen Verweise funktionieren sowohl bei einer eigenen Domain als auch unter einem GitHub-Pages-Projektpfad.

Die Veröffentlichung ist separat in [PUBLISHING.md](PUBLISHING.md) beschrieben.
