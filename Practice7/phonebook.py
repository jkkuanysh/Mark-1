"""Console PhoneBook application backed by PostgreSQL.

Features required by the practice:
- Create PhoneBook table
- Insert contacts from CSV
- Insert contacts from console
- Update contact name or phone
- Query with different filters
- Delete by username or phone
"""

import csv
from pathlib import Path
from typing import Optional

from connect import db_cursor


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS phonebook (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    phone VARCHAR(30) NOT NULL UNIQUE
);
"""


def create_table() -> None:
    """Create the phonebook table if it does not already exist."""
    with db_cursor(commit=True) as cur:
        cur.execute(CREATE_TABLE_SQL)
    print("Table 'phonebook' is ready.")


def add_contact(first_name: str, phone: str) -> None:
    """Insert one contact into the database."""
    sql = """
    INSERT INTO phonebook (first_name, phone)
    VALUES (%s, %s)
    ON CONFLICT (phone) DO NOTHING;
    """
    with db_cursor(commit=True) as cur:
        cur.execute(sql, (first_name.strip(), phone.strip()))
    print(f"Saved: {first_name} - {phone}")


def import_from_csv(file_path: str) -> None:
    """Load contacts from a CSV file.

    Expected CSV headers:
    first_name,phone
    """
    path = Path(file_path)
    if not path.exists():
        print("CSV file not found.")
        return

    imported = 0
    with path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = [(row["first_name"].strip(), row["phone"].strip()) for row in reader]

    if not rows:
        print("CSV file is empty.")
        return

    sql = """
    INSERT INTO phonebook (first_name, phone)
    VALUES (%s, %s)
    ON CONFLICT (phone) DO NOTHING;
    """
    with db_cursor(commit=True) as cur:
        cur.executemany(sql, rows)
        imported = cur.rowcount

    print(f"Imported {imported} contact(s) from CSV.")


def show_all_contacts() -> None:
    """Display all contacts in the table."""
    sql = "SELECT id, first_name, phone FROM phonebook ORDER BY first_name;"
    with db_cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()

    if not rows:
        print("PhoneBook is empty.")
        return

    print("\n--- ALL CONTACTS ---")
    for contact_id, first_name, phone in rows:
        print(f"{contact_id}. {first_name} - {phone}")


def search_by_name(name_part: str) -> None:
    """Search contacts by full or partial name."""
    sql = """
    SELECT id, first_name, phone
    FROM phonebook
    WHERE first_name ILIKE %s
    ORDER BY first_name;
    """
    with db_cursor() as cur:
        cur.execute(sql, (f"%{name_part.strip()}%",))
        rows = cur.fetchall()

    print_results(rows, f"Results for name containing '{name_part}'")


def search_by_phone_prefix(prefix: str) -> None:
    """Search contacts whose phone starts with a given prefix."""
    sql = """
    SELECT id, first_name, phone
    FROM phonebook
    WHERE phone LIKE %s
    ORDER BY first_name;
    """
    with db_cursor() as cur:
        cur.execute(sql, (f"{prefix.strip()}%",))
        rows = cur.fetchall()

    print_results(rows, f"Results for phone prefix '{prefix}'")


def print_results(rows, title: str) -> None:
    """Print query results in a readable format."""
    print(f"\n--- {title} ---")
    if not rows:
        print("No matching contacts found.")
        return

    for contact_id, first_name, phone in rows:
        print(f"{contact_id}. {first_name} - {phone}")


def find_contact_by_phone(phone: str) -> Optional[tuple]:
    """Return one contact row by exact phone number."""
    sql = "SELECT id, first_name, phone FROM phonebook WHERE phone = %s;"
    with db_cursor() as cur:
        cur.execute(sql, (phone.strip(),))
        return cur.fetchone()


def update_name_by_phone(phone: str, new_name: str) -> None:
    """Update a contact's name using their phone number."""
    sql = """
    UPDATE phonebook
    SET first_name = %s
    WHERE phone = %s;
    """
    with db_cursor(commit=True) as cur:
        cur.execute(sql, (new_name.strip(), phone.strip()))
        updated = cur.rowcount

    if updated:
        print("Name updated successfully.")
    else:
        print("No contact found with that phone number.")


def update_phone_by_name(old_name: str, new_phone: str) -> None:
    """Update a contact's phone number using their name."""
    sql = """
    UPDATE phonebook
    SET phone = %s
    WHERE first_name = %s;
    """
    with db_cursor(commit=True) as cur:
        cur.execute(sql, (new_phone.strip(), old_name.strip()))
        updated = cur.rowcount

    if updated:
        print("Phone updated successfully.")
    else:
        print("No contact found with that name.")


def delete_by_name(name: str) -> None:
    """Delete contacts by name."""
    sql = "DELETE FROM phonebook WHERE first_name = %s;"
    with db_cursor(commit=True) as cur:
        cur.execute(sql, (name.strip(),))
        deleted = cur.rowcount

    if deleted:
        print("Contact deleted successfully.")
    else:
        print("No contact found with that name.")


def delete_by_phone(phone: str) -> None:
    """Delete a contact by phone number."""
    sql = "DELETE FROM phonebook WHERE phone = %s;"
    with db_cursor(commit=True) as cur:
        cur.execute(sql, (phone.strip(),))
        deleted = cur.rowcount

    if deleted:
        print("Contact deleted successfully.")
    else:
        print("No contact found with that phone number.")


def menu() -> None:
    """Display the console menu until the user exits."""
    create_table()

    while True:
        print(
            """
====== PHONEBOOK MENU ======
1. Add contact from console
2. Import contacts from CSV
3. Show all contacts
4. Search by name
5. Search by phone prefix
6. Update contact name by phone
7. Update contact phone by name
8. Delete contact by name
9. Delete contact by phone
0. Exit
"""
        )

        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                first_name = input("Enter first name: ")
                phone = input("Enter phone number: ")
                add_contact(first_name, phone)

            elif choice == "2":
                file_path = input("Enter CSV file path: ")
                import_from_csv(file_path)

            elif choice == "3":
                show_all_contacts()

            elif choice == "4":
                name_part = input("Enter full or partial name: ")
                search_by_name(name_part)

            elif choice == "5":
                prefix = input("Enter phone prefix: ")
                search_by_phone_prefix(prefix)

            elif choice == "6":
                phone = input("Enter existing phone number: ")
                new_name = input("Enter new name: ")
                update_name_by_phone(phone, new_name)

            elif choice == "7":
                old_name = input("Enter existing name: ")
                new_phone = input("Enter new phone number: ")
                update_phone_by_name(old_name, new_phone)

            elif choice == "8":
                name = input("Enter name to delete: ")
                delete_by_name(name)

            elif choice == "9":
                phone = input("Enter phone to delete: ")
                delete_by_phone(phone)

            elif choice == "0":
                print("Goodbye!")
                break

            else:
                print("Invalid option. Please try again.")

        except Exception as error:
            print(f"Database error: {error}")


if __name__ == "__main__":
    menu()
