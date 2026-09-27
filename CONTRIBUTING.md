# Änderungen beitragen

Dieses Projekt erhält eine historische Dokumentation. Originalquellen und neu ergänzte Navigation sollen nachvollziehbar bleiben.

## Fehler melden

Bitte die Abschnittsnummer oder den Thementitel, das betroffene Format (HTML/PDF) und bei PDF-Problemen die Seitenzahl angeben. Bei Such- oder Darstellungsfehlern helfen Suchbegriff, Browser und Fenstergröße. Screenshots nach Möglichkeit ohne persönliche Daten hinzufügen.

## Änderungen vorbereiten

1. Einen eigenen Branch für die Änderung anlegen.
2. HTML/CSS/JavaScript in `scripts/` bearbeiten; die HTML-Ausgabe wird daraus generiert.
3. Nach [BUILD.md](docs/BUILD.md) neu bauen und die erzeugten Dateien prüfen.
4. Freigegebene Ergebnisse aus `build/Handbuch/` und `build/pdf/` in die entsprechenden Repository-Ordner übernehmen.
5. `python scripts/check_repository.py` ausführen und die betroffenen Seiten visuell kontrollieren.
6. Die Änderung im Changelog und im Pull Request erklären.

`Quellen/XMP1.HLP` und die Dateien in `Quellen/dekompiliert/` bilden das Originalarchiv. Inhaltliche Ergänzungen als solche kennzeichnen und mit einer Quelle belegen. Änderungen an technischen Aussagen dürfen nicht stillschweigend als unveränderter Originaltext erscheinen.

Die Dateien unter `Pruefung/` dokumentieren die ausgelieferte Ausgabe. Sie sind keine Live-Testergebnisse des aktuellen Arbeitsstands. Nach einer geänderten Ausgabe die Vollprüfung erneut durchführen und passende Protokolle aktualisieren.
