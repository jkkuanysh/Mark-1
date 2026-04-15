import os
from typing import List
from connect import get_connection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FUNCTIONS_SQL = os.path.join(BASE_DIR, "functions.sql")
PROCEDURES_SQL = os.path.join(BASE_DIR, "procedures.sql")


def run_sql_file(path: str) -> None:
    """Execute an SQL file to create functions/procedures/tables."""
    with open(path, "r", encoding="utf-8") as file:
        sql = file.read()

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql)
        conn.commit()
        print(f"Executed: {os.path.basename(path)}")
    except Exception as error:
        conn.rollback()
        print("Error while executing SQL file:", error)
    finally:
        cur.close()
        conn.close()


def setup_database() -> None:
    """Create all required database objects."""
    run_sql_file(FUNCTIONS_SQL)
    run_sql_file(PROCEDURES_SQL)


def upsert_contact() -> None:
    """Call stored procedure to insert or update one contact."""
    name = input("Enter name: ").strip()
    phone = input("Enter phone: ").strip()

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CALL upsert_contact(%s, %s)", (name, phone))
        conn.commit()
        print("Contact inserted/updated successfully.")
    except Exception as error:
        conn.rollback()
        print("Error:", error)
    finally:
        cur.close()
        conn.close()


def bulk_upsert() -> None:
    """Bulk insert/update contacts using arrays passed to a procedure."""
    print("Enter contacts one per line in format: name,phone")
    print("Press Enter on an empty line to finish.")

    names: List[str] = []
    phones: List[str] = []

    while True:
        line = input("> ").strip()
        if not line:
            break
        if "," not in line:
            print("Invalid format. Use: name,phone")
            continue
        name, phone = line.split(",", 1)
        names.append(name.strip())
        phones.append(phone.strip())

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CALL bulk_upsert_contacts(%s, %s)", (names, phones))
        conn.commit()
        print("Bulk procedure finished.")

        # Show incorrect rows stored by the procedure.
        cur.execute(
            """
            SELECT first_name, phone, reason
            FROM invalid_contacts
            ORDER BY id DESC
            LIMIT 20
            """
        )
        rows = cur.fetchall()
        if rows:
            print("\nIncorrect data returned by validation:")
            for row in rows:
                print(row)
        else:
            print("No incorrect data found.")
    except Exception as error:
        conn.rollback()
        print("Error:", error)
    finally:
        cur.close()
        conn.close()


def search_by_pattern() -> None:
    """Use the pattern-search function."""
    pattern = input("Enter search pattern: ").strip()

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM search_contacts_by_pattern(%s)", (pattern,))
        rows = cur.fetchall()
        if rows:
            print("\nMatched contacts:")
            for row in rows:
                print(row)
        else:
            print("No contacts found.")
    except Exception as error:
        print("Error:", error)
    finally:
        cur.close()
        conn.close()


def show_paginated() -> None:
    """Use the pagination function with LIMIT and OFFSET."""
    try:
        limit = int(input("Enter LIMIT: ").strip())
        offset = int(input("Enter OFFSET: ").strip())
    except ValueError:
        print("LIMIT and OFFSET must be integers.")
        return

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))
        rows = cur.fetchall()
        if rows:
            print("\nPaginated contacts:")
            for row in rows:
                print(row)
        else:
            print("No contacts on this page.")
    except Exception as error:
        print("Error:", error)
    finally:
        cur.close()
        conn.close()


def delete_contact() -> None:
    """Call procedure to delete by name or phone."""
    value = input("Enter name or phone to delete: ").strip()

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CALL delete_contact(%s)", (value,))
        conn.commit()
        print("Delete procedure executed.")
    except Exception as error:
        conn.rollback()
        print("Error:", error)
    finally:
        cur.close()
        conn.close()


def view_invalid_contacts() -> None:
    """Show rows that failed validation during bulk insert."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id, first_name, phone, reason, created_at FROM invalid_contacts ORDER BY id"
        )
        rows = cur.fetchall()
        if rows:
            print("\nInvalid contacts:")
            for row in rows:
                print(row)
        else:
            print("No invalid contacts stored.")
    except Exception as error:
        print("Error:", error)
    finally:
        cur.close()
        conn.close()


def menu() -> None:
    """Console menu for Practice 8."""
    while True:
        print("\n=== PHONEBOOK PRACTICE 8 ===")
        print("1. Setup database objects")
        print("2. Upsert one contact")
        print("3. Bulk upsert contacts")
        print("4. Search contacts by pattern")
        print("5. Show contacts with pagination")
        print("6. Delete contact by name or phone")
        print("7. View invalid contacts")
        print("0. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            setup_database()
        elif choice == "2":
            upsert_contact()
        elif choice == "3":
            bulk_upsert()
        elif choice == "4":
            search_by_pattern()
        elif choice == "5":
            show_paginated()
        elif choice == "6":
            delete_contact()
        elif choice == "7":
            view_invalid_contacts()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    menu()
