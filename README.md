# sql-automation

# Atruvia Demo – PostgreSQL + Python Automatisierung

---

## Zweck des Projekts
Dieses kleine Demo-Projekt wurde für meine Bewerbung erstellt, um **meine Fähigkeiten in PostgreSQL und Python** zu demonstrieren.  

Es zeigt:  
- Aufbau einer kleinen Datenbank (Kunden + Bestellungen)  
- Automatisches Einfügen neuer Bestellungen über Python  
- Berechnung eines Umsatzreports aus der Datenbank  

---



## Setup:

### 1) PostgreSQL vorbereiten
- Datenbank `atruvia_demo` erstellen
- Benutzer `atruvia_user` anlegen (Passwort z. B. `atruvia2026`) und Rechte vergeben (benötigt Berechtigung für 'TRUNCATE' und Daten einzufügen)

```sql
CREATE DATABASE atruvia_demo;
CREATE USER atruvia_user WITH PASSWORD 'atruvia2026';
GRANT ALL PRIVILEGES ON DATABASE atruvia_demo TO atruvia_user;
```

### 2) Python vorbereiten
- Python 3 muss installiert sein
- Installiere das benötigte Package für PostgreSQL:

```bash
pip install psycopg2-binary
```
