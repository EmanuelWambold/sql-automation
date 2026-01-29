# sql-automation

# Atruvia Demo – PostgreSQL + Python Automatisierung

---

## Zweck des Projekts
Dieses Demo-Projekt wurde im Rahmen meiner Bewerbung auf eine Werkstudentenstelle erstellt, um praktische Kenntnisse in **PostgreSQL** sowie **Python-basierter Datenbank-Automatisierung** zu demonstrieren.

**Funktionen:**
- Kunden/Bestellungen Datenbank mit ENUMs, Foreign Keys, Constraints
- Automatisches Hinzufügen neuer Bestellungen  
- Umsatz-Report pro Kunde (sortiert nach Gesamtumsatz)

---

## Projektstruktur
```text
sql-automation/
├── schema.sql      # Datenbankschema (Tabellen, ENUMs, Indizes)
├── main.py         # Hauptprogramm + Demo-Daten + Reports
└── README.md
```

## Setup (~2 Minuten)

### 1) PostgreSQL
```sql
CREATE DATABASE atruvia_demo;
CREATE USER atruvia_user WITH PASSWORD 'atruvia2026';
GRANT ALL PRIVILEGES ON DATABASE atruvia_demo TO atruvia_user;
```
Das Schema wird ausgeführt, indem `schema.sql` in pgAdmin gestartet wird.

### 2) Python
```bash
pip install psycopg2-binary
python main.py
```
Die Demo-Daten werden beim ersten Start automatisch eingefügt.

### 3) Erwartete Ausgabe
```text
--------------------------------------------------
ATRUVIA DEMO - PostgreSQL + Python automation
--------------------------------------------------

Demo data has been reset for (3 customers, 4 orders)

NEW ORDER: ID 5 for Max Mustermann

SALES REPORT:
   Fremder Unbekannter Kunde (Geheimstadt): 1 order(s), €1250.75
   Max Mustermann (Karlsruhe): 3 order(s), €770.60
   Emanuel Wambold (Woerth am Rhein): 1 order(s), €0.50


--------------------------------------------------
Demo completed
--------------------------------------------------
```
**Hinweis:** Der Gesamtumsatz von _Max Mustermann (Karlsruhe)_ variiert, da der Bestellbetrag zufällig generiert wird.

---

### Gelernte PostgreSQL Features
- ENUM-Typen (`order_status`)
- `TRUNCATE RESTART IDENTITY`
- `COALESCE` für NULL-Behandlung

### Gelernte Python Features
- Transaktionssteuerung mit `psycopg2`
- Type Hints
- `with conn:` für automatisches Commit und Rollback

---

## Status:
Aktiv weiterentwickelt nach Bewerbungseinsendung