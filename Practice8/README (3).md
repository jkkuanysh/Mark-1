# Practice 8 - PhoneBook with PostgreSQL Functions and Stored Procedures

## Files
- `phonebook.py` - console application
- `functions.sql` - PostgreSQL functions
- `procedures.sql` - PostgreSQL procedures
- `config.py` - database configuration
- `connect.py` - connection helper

## Features
- Pattern-search function
- Upsert procedure
- Bulk upsert procedure with validation
- Pagination function using LIMIT and OFFSET
- Delete procedure by name or phone
- Stores invalid bulk rows in `invalid_contacts`

## Setup
1. Create PostgreSQL database, for example: `phonebook_db`
2. Install dependency:
   ```bash
   pip install psycopg2-binary
   ```
3. Edit `config.py` and set your PostgreSQL credentials.
4. Run:
   ```bash
   python phonebook.py
   ```
5. Choose `1` first to create the SQL objects.

## Git commands
```bash
git add .
git commit -m "Add Practice8 - PhoneBook with functions and stored procedures"
git push origin main
```
