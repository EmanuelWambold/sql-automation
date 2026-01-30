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
├── README.md
├── main.py         # Hauptprogramm + Demo-Daten + Reports
└── schema.sql      # Datenbankschema (Tabellen, ENUMs, Indizes)
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


Demo data has been reset for (4 customers, 5 orders)

NEW ORDER: ID 6 for Max Mustermann
NEW ORDER: ID 7 for the newly created customer with ID 5

CUSTOMER SALES REPORT:
   Fremder Unbekannter Kunde (Geheimstadt): 1 order(s), 1250.75€
   Max Mustermann (Karlsruhe): 3 order(s), 832.57€
   Neuer Kunde (Unbekannt): 1 order(s), 99.99€
   Keine Stadt (Unbekannt): 1 order(s), 75.75€
   Emanuel Wambold (Woerth am Rhein): 1 order(s), 0.50€

CITY SALES REPORT - only 'shipped' and 'arrived' orders included:
   Karlsruhe: 1 order(s), 450.00€
   Unbekannt: 1 order(s), 75.75€
   Woerth am Rhein: 1 order(s), 0.50€
   Geheimstadt: 0 order(s), 0€

STATUS SALES REPORT:
  pending: 3 order(s), 1433.32€
  arrived: 2 order(s), 525.75€
  cancelled: 1 order(s), 299.99€
  shipped: 1 order(s), 0.50€


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