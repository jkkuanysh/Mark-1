# Practice 7 — Python & PostgreSQL PhoneBook

## Files
- `phonebook.py` — main console application
- `config.py` — database settings
- `connect.py` — connection helper and transaction handling
- `contacts.csv` — sample CSV file for import

## Requirements
Install PostgreSQL and a Python PostgreSQL driver first.
A quick way to install the driver is:

```bash
pip install psycopg2-binary
```

## 1. Create a database
Open PostgreSQL and create a database:

```sql
CREATE DATABASE phonebook_db;
```

## 2. Update config
Open `config.py` and set your PostgreSQL password.

Example:
```python
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "phonebook_db",
    "user": "postgres",
    "password": "your_password_here",
}
```

## 3. Run the program
```bash
python phonebook.py
```

The app will create the `phonebook` table automatically if it does not exist.

## Implemented requirements
- Create PhoneBook table
- Insert from CSV
- Insert from console
- Update name or phone
- Query with filters
- Delete by username or phone

## Suggested Git commands
```bash
git add .
git commit -m "Add Practice7 - PhoneBook with PostgreSQL"
git push origin main
```
