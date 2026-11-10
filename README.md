# Praktikum: Von lokalem Qualitätscheck zu Continuous Integration

**Werkzeuge:** VS Code, Git/GitHub, `uv`, Ruff, pytest, GitHub Actions  
**Arbeitsform:** einzeln oder zu zweit. Auch wenn zu zweit: jede Abgabe arbeitet in einem eigenen Fork (jede/r soll einmal bei sich eine CI erstellt haben und ausgeführt bekommen).

**Hilfe für yaml-Dateien**: Oft scheitert das Ausführen von GitHub Actions an kleinen Fehlern in der yaml-Datei. In solchen Fällen helfen kleine Tools die yaml-Dateien überprüfen, wie z.B. https://yamlchecker.com/yaml-formatter oder www.yamllint.com.

---

## Ziel

Ihr bekommt ein kleines Python-Projekt, das **fachlich bereits weitgehend funktioniert**. Die vorhandenen Tests sind grün. Der Code ist allerdings absichtlich schlecht formatiert und enthält mehrere typische Lint- und Lesbarkeitsprobleme.

Eure Aufgabe ist nicht, die Library neu zu schreiben. Ihr baut schrittweise einen automatisierten Qualitätsworkflow auf:

```text
Code im Repository
      ↓
Ruff Linting
      ↓
Ruff Formatting Check
      ↓
pytest
      ↓
Python 3.12 + Python 3.13
```

Am Ende gilt:

> Was ihr lokal prüfen könnt, wird bei jedem Push und Pull Request automatisch noch einmal reproduzierbar geprüft.

---

# Ausgangslage

Das Starter-Repository enthält ungefähr:

```text
mobility-stats-ci-starter/
├── .gitignore
├── README.md
├── pyproject.toml
├── data/
│   └── rides.csv
├── src/
│   └── mobility_stats/
│       ├── __init__.py
│       ├── rides.py
│       └── summary.py
└── tests/
    ├── test_rides.py
    └── test_summary.py
```

Die Library analysiert einige einfache Bike-Sharing-Daten. Beispielsweise kann sie:

- CSV-Daten einlesen,
- die durchschnittliche Fahrtdauer berechnen,
- Fahrten nach Nutzer:innen-Typ zählen,
- die häufigste Startstation bestimmen,
- lange Fahrten filtern,
- eine kleine Zusammenfassung erzeugen.

Die Tests sind bereits vorhanden. **Die CI fehlt absichtlich.**

---

# Phase 1 – Fork, Clone und Baseline

## 1. Fork erstellen

Öffnet das zentrale Starter-Repository auf GitHub.

Klickt:

```text
Fork
→ Create fork
```

Ihr arbeitet ab jetzt in **eurem eigenen Fork**.

Das zentrale Kurs-Repository bleibt unverändert.

---

## 2. Fork mit VS Code klonen

In VS Code:

```text
Ctrl+Shift+P / Cmd+Shift+P
→ Git: Clone
→ URL eures eigenen Forks einfügen
→ lokalen Ordner auswählen
→ Repository öffnen
```

Kontrolliert unten links in VS Code den aktuellen Branch.

Für dieses Praktikum arbeitet ihr **nicht direkt auf `main`**.

Erstellt über den Branchnamen unten links bzw. über die Command Palette:

```text
Git: Create Branch
```

Branchname:

```text
ci/quality-pipeline
```

---

## 3. Umgebung synchronisieren

Im integrierten VS-Code-Terminal:

```bash
uv sync
```

Falls im Starter-Repository noch kein `uv.lock` liegt, wird es dabei erzeugt.

**Das Lockfile gehört ins Repository.**

Prüft danach kurz:

```bash
uv run pytest
```

Erwartung:

```text
alle vorhandenen Tests sind grün
```

### Frage

Wenn alle Tests grün sind: Ist damit automatisch auch die Codequalität gut?

Schaut kurz in:

```text
src/mobility_stats/rides.py
src/mobility_stats/summary.py
```

Ihr solltet schnell sehen: eher nicht.

**Noch nichts reparieren.**

---

# Phase 2 – Erste CI: Ruff soll das Repository prüfen

## 4. Workflow-Datei anlegen

Erstellt in VS Code:

```text
.github/workflows/ci.yml
```

Falls die Ordner noch nicht existieren, legt sie ebenfalls an.

Beginnt mit diesem Workflow:

```yaml
name: Python CI

on:
  push:
  pull_request:

permissions:
  contents: read

jobs:
  quality:
    runs-on: ubuntu-latest

    steps:
      - name: Check out repository
        uses: actions/checkout@v7

      - name: Install uv
        uses: astral-sh/setup-uv@v10.0.0

      - name: Sync project
        run: uv sync --locked

      - name: Run Ruff linter
        run: uv run --locked ruff check .

      - name: Check formatting
        run: uv run --locked ruff format --check .
```

### Was tut dieser Workflow?

Versucht die drei Fragen zu beantworten:

1. **Wann** läuft er?   Er laeuft bei jedem ausgefuehrtem push und bei jedem pull-request
2. **Auf welchem Rechner** läuft er? Auf dem neusten Ubuntu System
3. **Welche lokalen Befehle** führt er dort aus? Check out repository, Install uv, sync project, run ruff linter, check formatting

Wichtig:

```text
CI repariert nichts.
CI prüft nur den committed Zustand.
```

Deshalb steht dort:

```bash
ruff check .
ruff format --check .
```

und **nicht**:

```bash
ruff check --fix .
ruff format .
```

---

## 5. Commit und Push über VS Code

Öffnet links **Source Control**.

Ihr solltet mindestens sehen:

```text
.github/workflows/ci.yml
uv.lock
```

Workflow:

```text
Source Control
→ Änderungen ansehen
→ Stage Changes (+)
→ Commit Message eingeben
→ Commit
→ Publish Branch / Push
```

Vorschlag für die Commit Message:

```text
Add initial Ruff CI workflow
```

Terminal-Alternative als Erinnerung:

```bash
git add .
git commit -m "Add initial Ruff CI workflow"
git push -u origin ci/quality-pipeline
```

---

## 6. Pull Request öffnen

Öffnet euren Fork auf GitHub.

Erstellt einen Pull Request:

```text
ci/quality-pipeline → main
```

**Nicht sofort mergen.**

Öffnet im Pull Request den Bereich der Checks / GitHub Actions.

### Erwartung

Der Workflow sollte **rot** werden.

Das ist hier Absicht.

---

## 7. Den Fehler nicht raten – Log lesen

Öffnet den fehlgeschlagenen Job.

Sucht nach Meldungen von Ruff.

Je nach Ruff-Version können beispielsweise Regeln erscheinen wie:

```text
F401   unused import
E401   multiple imports on one line
E711   comparison to None
E741   ambiguous variable name
I001   imports are incorrectly sorted
UP006  use built-in collection type
F841   local variable assigned but never used
```

Außerdem sollte der Formatting Check melden, dass Dateien nicht korrekt formatiert sind.

### Wichtig

Nicht einfach nur denken:

> CI ist kaputt.

Die CI macht gerade genau ihre Aufgabe:

> Sie zeigt, dass der committed Code unsere automatisierten Qualitätsregeln nicht erfüllt.

---

# Phase 3 – CI-Fehler lokal reproduzieren und reparieren

## 8. Dieselben Checks lokal ausführen

Zurück in VS Code.

Im Terminal:

```bash
uv run ruff check .
```

und:

```bash
uv run ruff format --check .
```

Die entscheidende Beobachtung:

```text
lokal                                 CI
------------------------------------------------------------
uv run ruff check .          <->      uv run --locked ruff check .
uv run ruff format --check . <->      uv run --locked ruff format --check .
```

CI verwendet keine geheimnisvolle andere Qualitätslogik.

---

## 9. Automatische Ruff-Fixes anwenden

Zuerst sicherstellen, dass ihr eure Änderungen mit Git nachvollziehen könnt.

In VS Code Source Control kurz ansehen, welche Dateien aktuell verändert sind.

Dann:

```bash
uv run ruff check --fix .
```

Direkt danach:

```bash
uv run ruff format .
```

**Jetzt nicht sofort committen.**

Öffnet in VS Code Source Control die Diffs.

Fragen:

- Welche Imports wurden entfernt oder sortiert?
  rides.py
    - Import sys wurde entfernt
    - type import entfernt und einfach dict staat Dict und list staat List benutzt
  summary.py
    - importete Funktionen nach Alphabet sotiert

- Welche Formatierungsänderungen wurden vorgenommen?
  rides.py
    - Leerzeichen um '=' ergaenzt, bei Aufzaehlungen und anderen Operatoren
    - Umformatierung des Dictionaries
  summary.py
    - Umformatierung des Dictionaries
    - Leerzeichen um Operatoren

- Welche Probleme konnte Ruff nicht selbst sinnvoll lösen?
  Die ungenutzte Variable unseencopy konnte Ruff nicht ohne Zustimmung entfernen

---

# 10. Human Cleanup: Ruff kann nicht alles entscheiden

Der Starter-Code enthält absichtlich auch Namen wie:

```python
a
b
c
p
x
```

Ein Formatter kann daraus nicht zuverlässig gute Namen machen.

Auch ein Linter weiß nicht automatisch, ob `a` fachlich eigentlich

```text
rides
```

oder

```text
station_counts
```

bedeuten soll.

Verbessert deshalb zusätzlich die Lesbarkeit.

Beispiele:

```text
a → rides
p → csv_path
x → rides
b → total_duration / counts / threshold
c → ride
l → long_rides
```

Ihr müsst nicht das komplette Design der Library verändern.

Ziel ist:

> Der Code soll nach dem Cleanup sowohl die automatisierten Regeln erfüllen als auch für Menschen deutlich verständlicher sein.

---

## 11. Qualitätschecks erneut ausführen

```bash
uv run ruff check .
uv run ruff format --check .
```

Beide sollten jetzt erfolgreich sein.

Aber bevor ihr pusht:

```bash
uv run pytest
```

Warum noch einmal Tests?

Weil automatische und manuelle Änderungen am Code ebenfalls Fehler verursachen können.

Der gewünschte lokale Zustand ist:

```text
pytest                     ✅
ruff check                 ✅
ruff format --check        ✅
```

---

## 12. Cleanup committen und pushen

Über VS Code Source Control:

```text
Diffs kontrollieren
→ Stage
→ Commit
→ Push / Sync Changes
```

Commit Message zum Beispiel:

```text
Fix Ruff findings and improve readability
```

Geht zurück zum Pull Request.

Die CI sollte automatisch erneut starten.

### Ziel

Der Ruff-Workflow wird jetzt **grün**.

---

# Phase 4 – Tests in die CI aufnehmen

Bisher prüft CI nur Codequalität und Formatierung.

Unsere vorhandenen Tests laufen nur lokal.

Das ändern wir jetzt.

## 13. pytest-Step ergänzen

Erweitert den vorhandenen Job nach dem Formatting Check:

```yaml
      - name: Run tests
        run: uv run --locked pytest -q
```

Der relevante Teil sieht anschließend aus wie:

```yaml
      - name: Run Ruff linter
        run: uv run --locked ruff check .

      - name: Check formatting
        run: uv run --locked ruff format --check .

      - name: Run tests
        run: uv run --locked pytest -q
```

Commit + Push wieder über VS Code.

Commit Message beispielsweise:

```text
Run pytest in CI
```

Beobachtet den Pull Request.

Jetzt automatisiert GitHub dieselben drei Fragen, die ihr lokal beantworten könnt:

```text
Ist der Code lint-clean?
Ist der Code korrekt formatiert?
Besteht die vorhandene Test-Suite?
```

---

# Phase 5 – Python-Versionen als Matrix

Bisher läuft der Workflow auf einem GitHub-Runner mit nur einer Python-Version.

Aber unser Projekt behauptet in `pyproject.toml`:

```toml
requires-python = ">=3.12"
```

Wir wollen deshalb zumindest zwei Python-Versionen automatisch prüfen:

```text
Python 3.12
Python 3.13
```

---

## 14. Matrix ergänzen

Erweitert euren Job:

```yaml
  quality:
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.12", "3.13"]

    runs-on: ubuntu-latest
```

Jetzt muss `setup-uv` wissen, welche Python-Version der jeweilige Matrix-Lauf verwenden soll:

```yaml
      - name: Install uv and Python
        uses: astral-sh/setup-uv@v10.0.0
        with:
          python-version: ${{ matrix.python-version }}
```

Damit wird derselbe komplette Job zweimal ausgeführt.

Einmal für:

```text
python-version = 3.12
```

und einmal für:

```text
python-version = 3.13
```

---

## 15. Commit und beobachten

Commit Message:

```text
Test project on multiple Python versions
```

Pushen.

Auf GitHub solltet ihr jetzt zwei Varianten des Jobs sehen.

Beide führen aus:

```text
checkout
→ setup uv + jeweilige Python-Version
→ uv sync --locked
→ ruff check
→ ruff format --check
→ pytest
```

### Frage

Warum ist die Matrix mehr als nur „zweimal denselben Test ausführen“?

Weil sie eine zusätzliche Behauptung unseres Projektes überprüft:

> Unser Code und unsere Dependencies funktionieren mit mehreren unterstützten Python-Versionen.

---

# Phase 6 – Abschluss 1 und Merge

## 16. Pull Request mergen

Erst wenn beide Matrix-Jobs grün sind:

```text
Pull Request
→ Merge
```

Danach lokal in VS Code wieder auf `main` wechseln und:

```text
Source Control → … → Pull
```

bzw. als Terminal-Erinnerung:

```bash
git switch main
git pull
```

---
# Phase 7 – Abschluss 2 und Merge

## 17. Weitere Anpassung: Strikter werden!

Einen "Linter" oder "Formatter" wie hier `ruff` können wir sehr detailiert anpassen, je nach unseren Vorstellungen und Anforderungen an das jeweilige Projekt.

Hier bitte einmal beispielhaft eine Auswahl an weiteren Regeln hinzufügen indem `"E"` bei euch lokal zur `extent-select` Liste in der `pyproject.toml` Datei hinzugefügt wird. Das steht dort unter der Kategorie `[tool.ruff.lint]`.

Danach bitte lokal noch einmal `uv run ruff check .` ausführen und schauen was passiert. Gibt es neue Hinweise/Beschwerden? Und wenn ja, machen die für euch Sinn? Diskutiert die Hinweise und sorg dann dafür dass ruff wieder "zufrieden" ist. Committed danach eure Änderungen.

## 18. Pull Request mergen

Sobald ruff nun wieder ohne Fehler läuft, die Änderungen zum remote pushen. Einen weiteren Pull Request erstellen und so lange weitere Anpassungen vornehmen, bis alle Tests grün sind. Danach in den `main`-Branch mergen. Done.

---


# Definition of Done

Das Praktikum ist abgeschlossen, wenn:

- [ ] ihr einen eigenen Fork erstellt und mit VS Code geklont habt,
- [ ] ihr auf einem Feature-Branch gearbeitet habt,
- [ ] `uv run pytest` lokal erfolgreich ist,
- [ ] ihr zunächst bewusst eine **rote Ruff-CI** gesehen habt,
- [ ] ihr den CI-Fehler im GitHub-Actions-Log gelesen habt,
- [ ] ihr dieselben Ruff-Checks lokal reproduziert habt,
- [ ] `ruff check --fix` und `ruff format` lokal verwendet wurden,
- [ ] ihr die Änderungen anschließend über Git-Diffs kontrolliert habt,
- [ ] schlecht verständliche Variablennamen zusätzlich manuell verbessert wurden,
- [ ] `uv run ruff check .` lokal grün ist,
- [ ] `uv run ruff format --check .` lokal grün ist,
- [ ] pytest Teil der CI ist,
- [ ] die CI auf Python 3.12 und 3.13 läuft,
- [ ] "E" zu den ruff-Settings in der pyproject.toml hinzugefügt ist,
- [ ] alle Matrix-Jobs grün sind,
- [ ] der Pull Request erst danach gemerged wurde.

---

# Abschlussfragen

Besprecht zum Schluss kurz:

1. Was ist der Unterschied zwischen `ruff check --fix .` und `ruff check .`?
2. Warum verwendet CI `ruff format --check .` und nicht `ruff format .`?
3. Was kann Ruff automatisch verbessern – und was nicht?
4. Warum führen wir nach automatischen Ruff-Fixes erneut pytest aus?
5. Was ist der Unterschied zwischen einem lokalen Testlauf und CI?
6. Was bedeutet ein grüner CI-Workflow **nicht**?
7. Welche zusätzliche Aussage überprüft eine Python-Versionen-Matrix?
8. Warum ist `uv.lock` für einen reproduzierbaren CI-Lauf hilfreich?

---

# Wenn ihr früher fertig seid

## Bonus A – CI absichtlich brechen

Ändert lokal kurz eine Erwartung in einem Test, sodass pytest fehlschlägt.

Führt zuerst lokal aus:

```bash
uv run pytest
```

Stellt danach den korrekten Test wieder her.

**Den absichtlich falschen Test nicht mergen.**

---

## Bonus B – Jobs sinnvoll trennen

Aktuell führt unsere Matrix sowohl Ruff als auch pytest für jede Python-Version aus.

Überlegt, ob das immer notwendig ist.

Eine professionellere Variante könnte sein:

```text
quality job
    ↓
ruff einmal

     +

test job
    ↓
Python 3.12
Python 3.13
```

Recherchiert dafür in GitHub Actions:

```yaml
needs:
```

und versucht, Quality und Kompatibilität in zwei Jobs aufzuteilen.

---
