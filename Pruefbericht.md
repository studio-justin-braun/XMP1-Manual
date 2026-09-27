# Prüfbericht zur Konvertierung von XMP1.HLP

Die Ausgabe rekonstruiert die bereitgestellte lokale Hilfedatei. Fachliche Inhalte wurden nicht aktualisiert oder ergänzt. Hinzugekommen sind Abschnittsnummerierung, Navigation, Suche, Stichwortregister und ein gemeinsames Design für HTML und PDF.

## Ausgangsdatei

- Datei: `XMP1.HLP`, 2.955.111 Bytes.
- SHA-256: `487089c8f0aab8dafafb1712b284400b90cec0411c963d2c4fbcf455cb6849f6`.
- Interner Titel: `MSP XMP1 Applikation Bedienhandb`.
- Originalvermerk: `® PET2BK`.
- Format: kompiliertes Windows-WinHelp; Projekt laut Decompiler für HC31/HCP.
- Interne Dateien: 135, davon zehn Inhalts-/Strukturdateien und 125 Bildressourcen.
- Keine eingebetteten Audio-, Video- oder zusätzlichen Baggage-Dateien vorhanden.

## Vollständigkeit und richtige Reihenfolge

| Bestandteil | Ergebnis |
| --- | --- |
| Hilfethemen | 244 von 244 übernommen, einschließlich Original-Inhaltsverzeichnis |
| Originale interne Verweise | 243 von 243 aufgelöst |
| Abbildungen | 125 von 125 an der Originalposition übernommen |
| Originalgrafiken | 106 BMP und 19 WMF zusätzlich unverändert beigelegt |
| Tabellen | 17 zusammenhängende Tabellen, 197 Zeilen, 1.106 Zellen |
| Stichwortregister | 276 Originaleinträge mit zugehörigen Themen |
| Hauptkapitel | 7, in der Reihenfolge des Original-Inhaltsverzeichnisses |

Die 243 Originalverweise bilden einen vollständigen, eindeutigen Themenbaum: Jedes der 243 Inhaltsthemen ist aus dem Inhaltsverzeichnis oder einem übergeordneten Thema erreichbar. Die Tiefensuche durch diesen Baum ergibt exakt die gespeicherte Reihenfolge der 244 Themen. Die ergänzte Nummerierung folgt dieser belegten Hierarchie. Kurze Dialog- und Detailthemen bleiben bei ihren jeweiligen Elternabschnitten. Die ursprüngliche WinHelp-Blätterfolge wurde zusätzlich ausgelesen; sie lässt einige dieser Detailseiten aus und wurde deshalb nicht als alleinige Sortiergrundlage verwendet.

Reihenfolge der Hauptkapitel:

1. Einleitung
2. Hauptmaske
3. XMP1 Konfiguration
4. XMP1 Bedienung
5. Soft-ABM-Befehle
6. Debugging
7. Planungswerte Strombedarf und thermische Verlustleistung

## Verfahren und Korrekturen

Zwei voneinander unabhängige Ausleseverfahren wurden verwendet:

- [winhlp 0.4.1](https://github.com/bitplane/winhlp) für das binäre Inventar, Themen, Stichwörter und einen unabhängigen Textvergleich.
- [HelpDeco 2.1](https://www.helpscribble.com/decompiler.html) für die Rückgewinnung von RTF, Projektdatei, Phrasen und Originalgrafiken.

Der erste HTML-Export aus winhlp enthielt bei dieser Quelldatei keine aktiven Querverweise. Außerdem wurden Absatzabstände fehlerhaft skaliert. Dieser Export wurde **nicht** als fertiges Handbuch verwendet. Die Ausgabe wurde aus der von HelpDeco erzeugten RTF-Struktur neu aufgebaut, einschließlich verborgener Linkziele, Schriftattributen, Absätzen, Tabellen und Bildmarkern.

Die sichtbaren Texte aller 244 Themen stimmen zwischen dem binären Parser und der RTF-Auswertung vollständig überein, wenn Leerraum vereinheitlicht wird. Symbolschrift-Aufzählungspunkte wurden als Unicode-Aufzählungspunkte wiedergegeben. Fettdruck, Kursivdruck, Unterstreichungen, Schrittfolgen und Zellzuordnungen bleiben erhalten; Schriften, Größen und Abstände wurden für zeitgemäße Lesbarkeit neu gesetzt.

Tabellen wurden anhand ihrer ursprünglichen RTF-Zellgrenzen zusammengesetzt. Geringfügig abweichende rechte Begrenzungen von übergreifenden Gruppenzeilen wurden derselben Spalte zugeordnet. Damit bleiben insbesondere die Zuordnung von Stromquelle und Stromsenke sowie die Spannungs-Unterspalten erhalten. Lange Tabellen wiederholen ihre Kopfzeilen auf Folgeseiten.

Die 19 WMF-Grafiken wurden mit Windows GDI+ bei 300 dpi rasterisiert. Die 106 BMP-Dateien wurden verlustfrei nach PNG übertragen. Für eine spätere vektorbasierte Weiterverarbeitung liegen alle originalen WMF-Dateien im Quellenordner bei.

## HTML-Prüfung

- Eine vollständig eigenständige HTML-Datei mit eingebetteten PNG-Bildern, CSS und JavaScript; keine CDN-, Schrift- oder Netzabhängigkeiten.
- 244 Themenabschnitte und 125 eingebettete Abbildungen.
- Alle lokalen Ankerverweise führen zu vorhandenen Zielen.
- Suche über Überschriften, Volltexte und Originalstichwörter; mehrere Wörter werden mit UND verknüpft.
- Groß-/Kleinschreibung und Umlautakzente werden für die Suche vereinheitlicht.
- Automatisierte Prüfung in einem separaten lokalen Chrome-Prozess: Suche, Trefferansicht, Hervorhebung, Trefferlinks, Umlautsuche, Mehrwortsuche, Nulltreffer, Zurücksetzen, Stichwortregister, Inhaltsnavigation, Originalverweise, Bildansicht, Schließen der Bildansicht, schmales Navigationsmenü, Startseite und Laden sämtlicher Bilder.
- Desktop- und schmale Fensterdarstellung geprüft; keine horizontale Überbreite der Gesamtseite in den geprüften Ansichten. Breite Tabellen können im schmalen Fenster separat horizontal gescrollt werden.

## PDF-Prüfung

- 132 A4-Seiten, durchsuchbarer Text und eingebettete Schriftarten.
- 125 platzierte Abbildungen.
- 254 Lesezeichen und 1.057 Linkannotationen einschließlich Navigation und Register.
- Alle sichtbaren Originaltextabsätze in der PDF-Textausgabe nachgewiesen, unter Vereinheitlichung von Leerraum und Aufzählungszeichen.
- Keine ungültigen internen Linkziele.
- Keine Textposition außerhalb der PDF-Seitenbegrenzungen.
- Alle Seiten gerendert und über Seitenübersichten visuell geprüft; zusätzliche Detailprüfung von Titelblatt, Tabellen, Diagrammen und Kapitelübergängen.

Maschinenlesbare Ergebnisse liegen unter `Pruefung/`. Die unveränderte Ausgangsdatei liegt unter `Quellen/`.

## Grenzen der Übertragung

Die Ausgabe bewahrt den historischen Stand der Quelle. Alte Betriebssystemangaben und Softwareanweisungen sind keine neu geprüfte Empfehlung für Windows 11. Die HLP-Anzeigefunktion `BrowseButtons()` wurde durch normale Inhalts- und Linknavigation ersetzt. Es gibt in dieser Datei keine ungelösten Themenverweise oder fehlenden Medienressourcen.

Screenshots behalten ihre ursprüngliche Auflösung. Bereits in den Originalbildern enthaltene Texte sind als Bildinhalt erhalten; die Volltextsuche durchsucht die extrahierten Hilfetexte und Stichwörter, nicht per OCR nachträglich erkannte Bildbeschriftungen. Im PDF ersetzt die Suchfunktion des PDF-Programms die interaktive HTML-Suche.
