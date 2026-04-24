"""
TSIS1: PhoneBook — Extended Contact Management

This console application extends the previous PhoneBook practices with:
- groups
- multiple phone numbers
- email
- birthday
- JSON import/export
- advanced filters and sorting
- console pagination
- new stored procedures and search function

Before running:
1. Install psycopg2-binary
2. Create a PostgreSQL database
3. Edit config.py with your connection settings
4. Run this script and choose "Setup database objects"
"""

import csv
import json
from datetime import datetime
from pathlib import Path

import psycopg2
from psycopg2 import sql

from connect import connect


ALLOWED_SORTS = {"name", "birthday", "date"}
ALLOWED_PHONE_TYPES = {"home", "work", "mobile"}


def execute_sql_file(filename: str) -> None:
    """Execute SQL commands from a file."""
    with connect() as conn:
        with conn.cursor() as cur:
            with open(filename, "r", encoding="utf-8") as f:
                cur.execute(f.read())
        conn.commit()
    print(f"Executed: {filename}")


def setup_database_objects() -> None:
    """Create tables and database-side objects."""
    base = Path(__file__).resolve().parent
    execute_sql_file(str(base / "schema.sql"))
    execute_sql_file(str(base / "procedures.sql"))
    print("Database schema and procedures are ready.")


def get_or_create_group(cur, group_name: str | None):
    """Return a group id. Create the group if needed."""
    if not group_name:
        return None

    cur.execute("SELECT id FROM groups WHERE LOWER(name) = LOWER(%s)", (group_name,))
    row = cur.fetchone()
    if row:
        return row[0]

    cur.execute(
        "INSERT INTO groups(name) VALUES (%s) RETURNING id",
        (group_name,),
    )
    return cur.fetchone()[0]


def get_contact_id(cur, name: str):
    """Return contact id by name, or None if not found."""
    cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
    row = cur.fetchone()
    return row[0] if row else None


def insert_or_update_contact(cur, name: str, email=None, birthday=None, group_name=None):
    """
    Insert a contact if it does not exist.
    If it exists, update the extra fields.
    """
    group_id = get_or_create_group(cur, group_name)
    contact_id = get_contact_id(cur, name)

    if contact_id:
        cur.execute(
            """
            UPDATE contacts
            SET email = COALESCE(%s, email),
                birthday = COALESCE(%s, birthday),
                group_id = COALESCE(%s, group_id)
            WHERE id = %s
            """,
            (email, birthday, group_id, contact_id),
        )
        return contact_id

    cur.execute(
        """
        INSERT INTO contacts(name, email, birthday, group_id)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (name, email, birthday, group_id),
    )
    return cur.fetchone()[0]


def add_phone_direct(cur, contact_id: int, phone: str, phone_type: str):
    """Insert a phone row directly after basic validation."""
    if phone_type not in ALLOWED_PHONE_TYPES:
        raise ValueError("Phone type must be home, work, or mobile.")

    cur.execute(
        """
        INSERT INTO phones(contact_id, phone, type)
        VALUES (%s, %s, %s)
        """,
        (contact_id, phone, phone_type),
    )


def import_csv(filename: str) -> None:
    """
    Import contacts from CSV.

    Expected columns:
    name,email,birthday,group_name,phone,phone_type
    """
    with connect() as conn:
        with conn.cursor() as cur:
            with open(filename, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    birthday = row["birthday"] or None
                    contact_id = insert_or_update_contact(
                        cur,
                        name=row["name"].strip(),
                        email=row.get("email") or None,
                        birthday=birthday,
                        group_name=row.get("group_name") or "Other",
                    )

                    phone = (row.get("phone") or "").strip()
                    phone_type = (row.get("phone_type") or "mobile").strip().lower()

                    if phone:
                        add_phone_direct(cur, contact_id, phone, phone_type)

        conn.commit()

    print("CSV import completed.")


def add_contact_from_console() -> None:
    """Insert one contact from user input."""
    name = input("Name: ").strip()
    email = input("Email: ").strip() or None
    birthday = input("Birthday (YYYY-MM-DD or empty): ").strip() or None
    group_name = input("Group (Family/Work/Friend/Other or custom): ").strip() or "Other"

    with connect() as conn:
        with conn.cursor() as cur:
            contact_id = insert_or_update_contact(cur, name, email, birthday, group_name)

            while True:
                phone = input("Phone (leave empty to stop): ").strip()
                if not phone:
                    break

                phone_type = input("Phone type (home/work/mobile): ").strip().lower()
                if phone_type not in ALLOWED_PHONE_TYPES:
                    print("Invalid type. Try again.")
                    continue

                add_phone_direct(cur, contact_id, phone, phone_type)

        conn.commit()

    print("Contact saved.")


def search_by_email() -> None:
    """Search contacts by partial email match."""
    query = input("Enter part of email: ").strip()

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT c.name, c.email, c.birthday, g.name,
                       COALESCE(STRING_AGG(p.phone || ' (' || p.type || ')', ', '), '')
                FROM contacts c
                LEFT JOIN groups g ON g.id = c.group_id
                LEFT JOIN phones p ON p.contact_id = c.id
                WHERE COALESCE(c.email, '') ILIKE %s
                GROUP BY c.id, c.name, c.email, c.birthday, g.name
                ORDER BY c.name
                """,
                (f"%{query}%",),
            )
            rows = cur.fetchall()

    print_contacts(rows)


def filter_by_group() -> None:
    """Display contacts from one selected group."""
    group_name = input("Enter group name: ").strip()

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT c.name, c.email, c.birthday, g.name,
                       COALESCE(STRING_AGG(p.phone || ' (' || p.type || ')', ', '), '')
                FROM contacts c
                JOIN groups g ON g.id = c.group_id
                LEFT JOIN phones p ON p.contact_id = c.id
                WHERE LOWER(g.name) = LOWER(%s)
                GROUP BY c.id, c.name, c.email, c.birthday, g.name
                ORDER BY c.name
                """,
                (group_name,),
            )
            rows = cur.fetchall()

    print_contacts(rows)


def list_sorted_contacts() -> None:
    """Sort output by name, birthday, or date added."""
    sort_choice = input("Sort by name / birthday / date: ").strip().lower()
    if sort_choice not in ALLOWED_SORTS:
        print("Invalid sort field.")
        return

    order_map = {
        "name": sql.SQL("c.name"),
        "birthday": sql.SQL("c.birthday NULLS LAST, c.name"),
        "date": sql.SQL("c.created_at DESC"),
    }

    with connect() as conn:
        with conn.cursor() as cur:
            query = sql.SQL(
                """
                SELECT c.name, c.email, c.birthday, g.name,
                       COALESCE(STRING_AGG(p.phone || ' (' || p.type || ')', ', '), '')
                FROM contacts c
                LEFT JOIN groups g ON g.id = c.group_id
                LEFT JOIN phones p ON p.contact_id = c.id
                GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
                ORDER BY {}
                """
            ).format(order_map[sort_choice])

            cur.execute(query)
            rows = cur.fetchall()

    print_contacts(rows)


def paginated_navigation(page_size: int = 3) -> None:
    """
    Console pagination loop.
    This tries to use the Practice 8 pagination function if it exists.
    If that function is absent, it falls back to direct LIMIT/OFFSET query.
    """
    offset = 0

    while True:
        with connect() as conn:
            with conn.cursor() as cur:
                try:
                    # Existing DB pagination function from Practice 8.
                    cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (page_size, offset))
                    rows = cur.fetchall()
                    # Practice 8 function may only return name/phone style rows.
                    normalized_rows = []
                    for row in rows:
                        if len(row) == 2:
                            normalized_rows.append((row[0], None, None, None, row[1]))
                        else:
                            normalized_rows.append(row)
                    rows = normalized_rows
                except psycopg2.Error:
                    conn.rollback()
                    cur.execute(
                        """
                        SELECT c.name, c.email, c.birthday, g.name,
                               COALESCE(STRING_AGG(p.phone || ' (' || p.type || ')', ', '), '')
                        FROM contacts c
                        LEFT JOIN groups g ON g.id = c.group_id
                        LEFT JOIN phones p ON p.contact_id = c.id
                        GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
                        ORDER BY c.name
                        LIMIT %s OFFSET %s
                        """,
                        (page_size, offset),
                    )
                    rows = cur.fetchall()

        print(f"\n--- Page offset {offset} ---")
        print_contacts(rows)

        command = input("next / prev / quit: ").strip().lower()
        if command == "next":
            offset += page_size
        elif command == "prev":
            offset = max(0, offset - page_size)
        elif command == "quit":
            break
        else:
            print("Unknown command.")


def export_to_json(filename: str) -> None:
    """Export all contacts, phones, and groups to a JSON file."""
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    c.id,
                    c.name,
                    c.email,
                    c.birthday,
                    c.created_at,
                    COALESCE(g.name, 'Other') AS group_name
                FROM contacts c
                LEFT JOIN groups g ON g.id = c.group_id
                ORDER BY c.name
                """
            )
            contacts = cur.fetchall()

            result = []
            for contact_id, name, email, birthday, created_at, group_name in contacts:
                cur.execute(
                    "SELECT phone, type FROM phones WHERE contact_id = %s ORDER BY id",
                    (contact_id,),
                )
                phones = [{"phone": p, "type": t} for p, t in cur.fetchall()]

                result.append(
                    {
                        "name": name,
                        "email": email,
                        "birthday": birthday.isoformat() if birthday else None,
                        "created_at": created_at.isoformat() if created_at else None,
                        "group": group_name,
                        "phones": phones,
                    }
                )

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f"Exported to {filename}")


def import_from_json(filename: str) -> None:
    """
    Import contacts from JSON.
    On duplicate (same name), user chooses skip or overwrite.
    """
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    with connect() as conn:
        with conn.cursor() as cur:
            for item in data:
                name = item["name"]
                email = item.get("email")
                birthday = item.get("birthday")
                group_name = item.get("group", "Other")
                phones = item.get("phones", [])

                contact_id = get_contact_id(cur, name)

                if contact_id:
                    action = input(f'Contact "{name}" exists. skip or overwrite? ').strip().lower()
                    if action == "skip":
                        continue
                    if action == "overwrite":
                        group_id = get_or_create_group(cur, group_name)
                        cur.execute(
                            """
                            UPDATE contacts
                            SET email = %s,
                                birthday = %s,
                                group_id = %s
                            WHERE id = %s
                            """,
                            (email, birthday, group_id, contact_id),
                        )
                        cur.execute("DELETE FROM phones WHERE contact_id = %s", (contact_id,))
                    else:
                        print("Unknown option. Skipping.")
                        continue
                else:
                    contact_id = insert_or_update_contact(cur, name, email, birthday, group_name)

                for phone_info in phones:
                    phone = phone_info.get("phone")
                    phone_type = phone_info.get("type", "mobile")
                    if phone and phone_type in ALLOWED_PHONE_TYPES:
                        add_phone_direct(cur, contact_id, phone, phone_type)

        conn.commit()

    print("JSON import completed.")


def call_add_phone_procedure() -> None:
    """Call the add_phone stored procedure."""
    name = input("Contact name: ").strip()
    phone = input("Phone: ").strip()
    phone_type = input("Type (home/work/mobile): ").strip().lower()

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, phone_type))
        conn.commit()

    print("Phone added using stored procedure.")


def call_move_to_group_procedure() -> None:
    """Call the move_to_group stored procedure."""
    name = input("Contact name: ").strip()
    group_name = input("New group name: ").strip()

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL move_to_group(%s, %s)", (name, group_name))
        conn.commit()

    print("Contact moved using stored procedure.")


def call_search_contacts_function() -> None:
    """Call the DB function that searches by name, email, and phones."""
    query = input("Enter search text: ").strip()

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s)", (query,))
            rows = cur.fetchall()

    # Return format already fits the display helper after trimming id/created_at.
    display_rows = [(r[1], r[2], r[3], r[4], r[6]) for r in rows]
    print_contacts(display_rows)


def print_contacts(rows) -> None:
    """Pretty print contacts in a simple console table."""
    if not rows:
        print("No contacts found.")
        return

    print("-" * 110)
    print(f"{'Name':20} {'Email':28} {'Birthday':12} {'Group':12} Phones")
    print("-" * 110)

    for row in rows:
        name, email, birthday, group_name, phones = row
        birthday_str = str(birthday) if birthday else ""
        print(f"{str(name):20} {str(email or ''):28} {birthday_str:12} {str(group_name or ''):12} {phones}")

    print("-" * 110)


def show_menu() -> None:
    """Main console menu."""
    while True:
        print("""
1. Setup database objects
2. Import contacts from CSV
3. Add contact from console
4. Filter contacts by group
5. Search contacts by email
6. Sort contacts
7. Paginated navigation
8. Export all contacts to JSON
9. Import contacts from JSON
10. Add phone (stored procedure)
11. Move contact to group (stored procedure)
12. Search contacts across all fields (DB function)
0. Exit
""")
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                setup_database_objects()
            elif choice == "2":
                filename = input("CSV filename [contacts.csv]: ").strip() or "contacts.csv"
                import_csv(filename)
            elif choice == "3":
                add_contact_from_console()
            elif choice == "4":
                filter_by_group()
            elif choice == "5":
                search_by_email()
            elif choice == "6":
                list_sorted_contacts()
            elif choice == "7":
                paginated_navigation()
            elif choice == "8":
                filename = input("JSON filename [contacts_export.json]: ").strip() or "contacts_export.json"
                export_to_json(filename)
            elif choice == "9":
                filename = input("JSON filename: ").strip()
                import_from_json(filename)
            elif choice == "10":
                call_add_phone_procedure()
            elif choice == "11":
                call_move_to_group_procedure()
            elif choice == "12":
                call_search_contacts_function()
            elif choice == "0":
                print("Goodbye.")
                break
            else:
                print("Invalid option.")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    show_menu()
