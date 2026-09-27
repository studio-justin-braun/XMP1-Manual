# Repository auf GitHub bereitstellen

Diese Anleitung beschreibt die Veröffentlichung der lokal vorbereiteten Dateien. Die Einrichtung selbst erzeugt weder ein GitHub-Repository noch einen Remote oder eine öffentliche Website.

## Repository übertragen

In GitHub Desktop das vorhandene lokale Repository `XMP1-Manual` hinzufügen, die Änderungen prüfen und committen. Anschließend **Publish repository** verwenden und den gewünschten Eigentümer sowie die Sichtbarkeit wählen.

Bei Nutzung der Kommandozeile nach dem Anlegen eines leeren GitHub-Repositorys:

```powershell
git status
git add .
git commit -m "Add complete XMP1 manual and repository tooling"
git remote add origin https://github.com/OWNER/XMP1-Manual.git
git push -u origin main
```

`OWNER` durch den tatsächlichen Account- oder Organisationsnamen ersetzen. Existiert bereits ein Remote, zuerst `git remote -v` prüfen. Es ist kein Accountname fest in den Dateien hinterlegt.

## GitHub Pages aktivieren

1. Im GitHub-Repository **Settings → Pages** öffnen.
2. Unter **Build and deployment → Source** **GitHub Actions** wählen.
3. **Actions → GitHub Pages → Run workflow** auf dem Standardbranch starten.
4. Die Website-Adresse dem abgeschlossenen Deployment entnehmen.

Der Workflow prüft die vorhandene Ausgabe, kopiert die Website-Dateien nach `build/site/` und veröffentlicht genau diesen Ordner. `Quellen/`, Build-Skripte und Arbeitsdateien werden nicht in das Pages-Artefakt kopiert; sie bleiben Teil des Git-Repositorys und sind bei einem öffentlichen Repository dort zugänglich.

Die Pages-Veröffentlichung wird manuell ausgelöst. Pushes und Pull Requests starten nur die Validierung. Ein auf einem anderen Branch gestarteter Pages-Lauf überspringt die Veröffentlichung.

Referenz: [GitHub-Dokumentation zu eigenen Pages-Workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## Download als Release anbieten

Lokal `python scripts/package_manual.py` ausführen. Danach kann `dist/XMP1_Handbuch_Gesamtpaket.zip` zusammen mit der PDF als Anhang eines GitHub-Releases hochgeladen werden. Ein Tag oder Release wird durch die lokalen Skripte nicht automatisch erstellt.

Empfohlene Repository-Beschreibung:

> Vollständiges MSP-XMP1-Bedienhandbuch aus WinHelp: Offline-HTML mit Suche, 132-seitige PDF und Originalquellen.

Passende Topics: `xmp1`, `winhelp`, `documentation`, `manual`, `legacy-documentation`, `offline`, `telecommunications`.
