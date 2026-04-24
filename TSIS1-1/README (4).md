# TSIS1 - PhoneBook Extended Contact Management

## Files
- `phonebook.py` - main console application
- `config.py` - PostgreSQL connection settings
- `connect.py` - database connection helper
- `schema.sql` - schema extension for contacts, groups, phones
- `procedures.sql` - new procedures and function
- `contacts.csv` - sample CSV with new fields

## Features completed
- updated schema with:
  - `groups` table
  - `phones` table
  - `email` field
  - `birthday` field
- filter by group
- search by email
- sort by name / birthday / date added
- paginated navigation
- export contacts to JSON
- import contacts from JSON with duplicate handling
- procedure `add_phone`
- procedure `move_to_group`
- function `search_contacts`

## How to run

1. Install package:
```bash
pip install psycopg2-binary
```

2. Edit `config.py` with your PostgreSQL credentials.

3. Run:
```bash
python phonebook.py
```

4. In the menu choose:
- `1` to create schema and procedures
- `2` to import sample CSV
- other options for search, sort, JSON, and procedures

## Suggested Git commands
```bash
git add .
git commit -m "Add TSIS1 - extended phonebook"
git push origin main
```
