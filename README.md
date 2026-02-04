# sql-automation

## Atruvia Demo – PostgreSQL + Python Automatisierung

---

## Zweck des Projekts
Dieses Demo-Projekt wurde für meine Werkstudenten-Bewerbung erstellt, um praktische Kenntnisse in **PostgreSQL** und **Python-Datenbankautomatisierung** zu demonstrieren.

**Features:**
- Vollständige Kunden-/Bestellungs-Datenbank mit ENUMs, Foreign Keys, Constraints und Views
- Automatisches Hinzufügen von Bestellungen an bestehende Kunden
- Transaktionssichere Erstellung neuer Kunden mit erster Bestellung
- Mehrere Reports: Umsatz pro Kunde (über View), pro Stadt (Status gefiltert), pro Status, Datumsbereich

---

## Projektstruktur
```text
sql-automation/
├── data/
│   └── schema.sql          # Datenbankschema (Tabellen, ENUMs, Views, Index)
│
├── src/
│   ├── __init__.py         # Python-Package für saubere Imports
│   ├── connection.py       # get_connection() + Environment-Management
│   ├── repository.py       # Repository-Pattern: Alle CRUD + Reports
│   └── validation.py       # validate_param_type()
│
├── .env.example           # Konfiguration-Vorlage (DB-Zugangsdaten)
├── .gitignore             # Schützt .env (Passwort)
├── README.md
└── main.py                # Demo-Runner
```

## Setup (~2 Minuten)

### 1) Umgebungsvariablen (Sicherheit)
Dieses Projekt nutzt Umgebungsvariablen für die Datenbank-Konfiguration.
1. Installiere die benötigten Abhängigkeiten:
```bash
pip install psycopg2-binary python-dotenv
```
2. Kopiere die Beispieldatei: `.env.example` zu `.env`
3. Passe die Werte in der .env Datei an dein lokales PostgreSQL-Setup an.

### 2) PostgreSQL
Erstelle die Datenbank und den User (Beispielwerte aus `.env.example`):
```sql
CREATE DATABASE your_database_name_here;
CREATE USER your_db_user_here WITH PASSWORD 'your_db_password_here';
GRANT ALL PRIVILEGES ON DATABASE your_database_name_here TO your_db_user_here;
```
Das Schema wird ausgeführt, indem `schema.sql` in pgAdmin oder per psql gestartet wird.

### 3) Programm starten
```bash
cd sql-automation
python main.py
```
Die Demo-Daten werden beim ersten Start automatisch eingefügt.

### 4) Erwartete Ausgabe
```text
--------------------------------------------------
ATRUVIA DEMO - PostgreSQL + Python automation
--------------------------------------------------


Demo data has been reset for (4 customers, 5 orders)

NEW ORDER: ID 6 for Max Mustermann
NEW ORDER: ID 7 for the newly created customer with ID 5

CUSTOMER SALES REPORT:
   Fremder Unbekannter Kunde (Geheimstadt): 1 order(s), 1250.75€
   Max Mustermann (Karlsruhe): 3 order(s), 795.96€
   Neuer Kunde (Unbekannt): 1 order(s), 99.99€
   Keine Stadt (Unbekannt): 1 order(s), 75.75€
   Emanuel Wambold (Woerth am Rhein): 1 order(s), 0.50€

CITY SALES REPORT - only 'shipped' and 'arrived' orders included:
   Karlsruhe: 1 order(s), 450.00€
   Unbekannt: 1 order(s), 75.75€
   Woerth am Rhein: 1 order(s), 0.50€
   Geheimstadt: 0 order(s), 0€

STATUS SALES REPORT:
   pending: 3 order(s), 1396.71€
   arrived: 2 order(s), 525.75€
   cancelled: 1 order(s), 299.99€
   shipped: 1 order(s), 0.50€

REVENUE BETWEEN 2025-12-01 AND 2026-01-25:
   Total revenue: 450.50€


--------------------------------------------------
Demo completed
--------------------------------------------------
```
**Hinweis:** Der Gesamtumsatz von _Max Mustermann (Karlsruhe)_ variiert, da der Bestellbetrag zufällig generiert wird.

---

## Verwendete Python / psycopg2 Features

- Direkte PostgreSQL-Anbindung mit `psycopg2`
- `RealDictCursor` für dictionary-ähnliche Row-Zugriffe
- Transaktionssteuerung mit `with conn:` (automatisches Commit/Rollback)
- Parametrisierte Abfragen (`%s`-Platzhalter) für SQL-Injection-Schutz
- `INSERT ... RETURNING id` für verknüpfte Records in einer Transaktion
- Parameter-Validierung mit `validate_param_type()` (Type Hints + NULL-Support)
- Datumsformat-Validierung mit `datetime.strptime('%Y-%m-%d')`
- Strukturierte Fehlerbehandlung mit `try/except` zu allen DB-Operationen
- Getrennte Verantwortlichkeiten:
  - `reset_demo()` für Schema-Reset + Demo-Daten
  - `add_order()` und `insert_new_customer_with_first_order()` für Business-Logik
  - Mehrere Report-Funktionen (pro Kunde, Stadt, Status, Datumsbereich)
- Repository-Pattern in `src/repository.py` mit `cursor.executemany()` für Bulk-Inserts
- Modulare Architektur: `src/connection.py`, `src/validation.py`, `main.py`


## Verwendete SQL / PostgreSQL Features

- PostgreSQL als primäre Datenbank
- Eigener ENUM-Typ `order_status` für Bestellstatus
- SERIAL PRIMARY KEY für Auto-Increment IDs
- CHECK-Constraint `amount >= 0` zur Datensicherheit
- Foreign Key `orders.customer_id` mit `ON DELETE CASCADE`
- Index auf `orders.order_date` für Datumsbereich-Abfragen
- Automatische Timestamps mit `DEFAULT CURRENT_TIMESTAMP`
- Automatische Datumswerte mit `DEFAULT CURRENT_DATE`
- Aggregationen mit `SUM`/`COUNT` über verknüpfte Tabellen
- NULL-Behandlung mit `COALESCE`, z.B. `COALESCE(city, 'Unbekannt')`
- Bedingte Aggregationen mit `CASE WHEN`
- SQL-View `customer_revenue_view` für gekapselte Kundenumsatz-Berichte
- `TRUNCATE ... RESTART IDENTITY CASCADE` für Demo-Reset
- `cursor.executemany()` für performante Bulk-Insert-Operationen

---

## Status:
**Aktiv weiterentwickelt** nach Bewerbungseinsendung