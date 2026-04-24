import csv
import json
import os
import sys
import psycopg2
from connect import get_connection


def execute_sql_file(filename):
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return

    conn = get_connection()
    cur = conn.cursor()

    with open(filename, "r", encoding="utf-8") as file:
        sql = file.read()

    try:
        cur.execute(sql)
        conn.commit()
        print(f"{filename} executed successfully.")
    except Exception as e:
        conn.rollback()
        print("SQL error:", e)
    finally:
        cur.close()
        conn.close()


def setup_database():
    execute_sql_file("schema.sql")
    execute_sql_file("procedures.sql")


def print_rows(rows):
    if not rows:
        print("No results.")
        return

    for row in rows:
        print("-" * 80)
        print(row)


def add_contact():
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    birthday = input("Birthday (YYYY-MM-DD or empty): ").strip()
    group = input("Group (Family/Work/Friend/Other): ").strip() or "Other"
    phone = input("Phone: ").strip()
    phone_type = input("Phone type (home/work/mobile): ").strip().lower() or "mobile"

    if phone_type not in ["home", "work", "mobile"]:
        print("Invalid phone type.")
        return

    birthday_value = birthday if birthday else None

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO groups(name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (group,))
        cur.execute("SELECT id FROM groups WHERE name = %s", (group,))
        group_id = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO contacts(name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (name, email, birthday_value, group_id))

        contact_id = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO phones(contact_id, phone, type)
            VALUES (%s, %s, %s)
        """, (contact_id, phone, phone_type))

        conn.commit()
        print("Contact added successfully.")

    except Exception as e:
        conn.rollback()
        print("Error:", e)

    finally:
        cur.close()
        conn.close()


def add_phone_to_contact():
    name = input("Contact name: ").strip()
    phone = input("New phone: ").strip()
    phone_type = input("Type (home/work/mobile): ").strip().lower()

    if phone_type not in ["home", "work", "mobile"]:
        print("Invalid phone type.")
        return

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, phone_type))
        conn.commit()
        print("Phone added.")
    except Exception as e:
        conn.rollback()
        print("Error:", e)
    finally:
        cur.close()
        conn.close()


def move_contact_group():
    name = input("Contact name: ").strip()
    group = input("New group: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("CALL move_to_group(%s, %s)", (name, group))
        conn.commit()
        print("Contact moved.")
    except Exception as e:
        conn.rollback()
        print("Error:", e)
    finally:
        cur.close()
        conn.close()


def search_contacts_console():
    query = input("Search by name/email/phone/group: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM search_contacts(%s)", (query,))
        rows = cur.fetchall()
        print_rows(rows)
    except Exception as e:
        print("Error:", e)
    finally:
        cur.close()
        conn.close()


def filter_by_group():
    group = input("Group name: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.id, c.name, c.email, c.birthday, g.name,
               COALESCE(string_agg(p.phone || ' (' || p.type || ')', ', '), '') AS phones
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        WHERE g.name ILIKE %s
        GROUP BY c.id, c.name, c.email, c.birthday, g.name
        ORDER BY c.name
    """, (group,))

    rows = cur.fetchall()
    print_rows(rows)

    cur.close()
    conn.close()


def sort_contacts():
    allowed = {
        "1": "name",
        "2": "birthday",
        "3": "created_at"
    }

    print("Sort by:")
    print("1. Name")
    print("2. Birthday")
    print("3. Date added")

    choice = input("Choose: ").strip()
    sort_by = allowed.get(choice, "name")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM get_contacts_page(%s, %s, %s)", (100, 0, sort_by))
    rows = cur.fetchall()
    print_rows(rows)

    cur.close()
    conn.close()


def paginated_navigation():
    limit = 5
    offset = 0
    sort_by = "name"

    while True:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM get_contacts_page(%s, %s, %s)", (limit, offset, sort_by))
        rows = cur.fetchall()

        print("\nPAGE")
        print_rows(rows)

        cur.close()
        conn.close()

        command = input("\nnext / prev / sort / quit: ").strip().lower()

        if command == "next":
            offset += limit
        elif command == "prev":
            offset = max(0, offset - limit)
        elif command == "sort":
            sort_by = input("Sort by name/birthday/created_at: ").strip()
            if sort_by not in ["name", "birthday", "created_at"]:
                sort_by = "name"
            offset = 0
        elif command == "quit":
            break


def export_to_json():
    filename = input("Output JSON file (default contacts.json): ").strip() or "contacts.json"

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            c.id,
            c.name,
            c.email,
            c.birthday,
            c.created_at,
            g.name AS group_name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY c.name
    """)

    contacts = []

    for contact in cur.fetchall():
        contact_id, name, email, birthday, created_at, group_name = contact

        cur.execute("SELECT phone, type FROM phones WHERE contact_id = %s", (contact_id,))
        phones = [{"phone": p[0], "type": p[1]} for p in cur.fetchall()]

        contacts.append({
            "name": name,
            "email": email,
            "birthday": str(birthday) if birthday else None,
            "created_at": str(created_at) if created_at else None,
            "group": group_name,
            "phones": phones
        })

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(contacts, file, indent=4, ensure_ascii=False)

    print(f"Exported to {filename}")

    cur.close()
    conn.close()


def import_from_json():
    filename = input("Input JSON file (default contacts.json): ").strip() or "contacts.json"

    if not os.path.exists(filename):
        print("File not found.")
        return

    with open(filename, "r", encoding="utf-8") as file:
        contacts = json.load(file)

    conn = get_connection()
    cur = conn.cursor()

    try:
        for item in contacts:
            name = item["name"]
            email = item.get("email")
            birthday = item.get("birthday")
            group = item.get("group") or "Other"
            phones = item.get("phones", [])

            cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
            existing = cur.fetchone()

            if existing:
                action = input(f"{name} already exists. skip/overwrite? ").strip().lower()

                if action == "skip":
                    continue

                if action == "overwrite":
                    cur.execute("DELETE FROM contacts WHERE name = %s", (name,))
                else:
                    print("Unknown action. Skipping.")
                    continue

            cur.execute("INSERT INTO groups(name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (group,))
            cur.execute("SELECT id FROM groups WHERE name = %s", (group,))
            group_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO contacts(name, email, birthday, group_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (name, email, birthday, group_id))

            contact_id = cur.fetchone()[0]

            for phone_item in phones:
                phone = phone_item.get("phone")
                phone_type = phone_item.get("type", "mobile")

                if phone and phone_type in ["home", "work", "mobile"]:
                    cur.execute("""
                        INSERT INTO phones(contact_id, phone, type)
                        VALUES (%s, %s, %s)
                    """, (contact_id, phone, phone_type))

        conn.commit()
        print("JSON imported successfully.")

    except Exception as e:
        conn.rollback()
        print("Error:", e)

    finally:
        cur.close()
        conn.close()


def import_from_csv():
    filename = input("CSV file (default contacts.csv): ").strip() or "contacts.csv"

    if not os.path.exists(filename):
        print("File not found.")
        return

    conn = get_connection()
    cur = conn.cursor()

    try:
        with open(filename, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                name = row["name"].strip()
                email = row.get("email", "").strip()
                birthday = row.get("birthday", "").strip() or None
                group = row.get("group", "Other").strip() or "Other"
                phone = row.get("phone", "").strip()
                phone_type = row.get("type", "mobile").strip().lower()

                if phone_type not in ["home", "work", "mobile"]:
                    print(f"Skipping invalid phone type for {name}")
                    continue

                cur.execute("INSERT INTO groups(name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (group,))
                cur.execute("SELECT id FROM groups WHERE name = %s", (group,))
                group_id = cur.fetchone()[0]

                cur.execute("""
                    INSERT INTO contacts(name, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (name)
                    DO UPDATE SET email = EXCLUDED.email,
                                  birthday = EXCLUDED.birthday,
                                  group_id = EXCLUDED.group_id
                    RETURNING id
                """, (name, email, birthday, group_id))

                contact_id = cur.fetchone()[0]

                if phone:
                    cur.execute("""
                        INSERT INTO phones(contact_id, phone, type)
                        VALUES (%s, %s, %s)
                    """, (contact_id, phone, phone_type))

        conn.commit()
        print("CSV imported successfully.")

    except Exception as e:
        conn.rollback()
        print("Error:", e)

    finally:
        cur.close()
        conn.close()


def delete_contact():
    name = input("Contact name to delete: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM contacts WHERE name = %s", (name,))
    conn.commit()

    print("Deleted if contact existed.")

    cur.close()
    conn.close()


def main_menu():
    while True:
        print("\n" + "=" * 40)
        print("TSIS1 EXTENDED PHONEBOOK")
        print("=" * 40)
        print("1. Setup database")
        print("2. Add contact")
        print("3. Add phone to contact")
        print("4. Move contact to group")
        print("5. Search contacts")
        print("6. Filter by group")
        print("7. Sort contacts")
        print("8. Paginated navigation")
        print("9. Export to JSON")
        print("10. Import from JSON")
        print("11. Import from CSV")
        print("12. Delete contact")
        print("0. Exit")

        choice = input("Choose: ").strip()

        if choice == "1":
            setup_database()
        elif choice == "2":
            add_contact()
        elif choice == "3":
            add_phone_to_contact()
        elif choice == "4":
            move_contact_group()
        elif choice == "5":
            search_contacts_console()
        elif choice == "6":
            filter_by_group()
        elif choice == "7":
            sort_contacts()
        elif choice == "8":
            paginated_navigation()
        elif choice == "9":
            export_to_json()
        elif choice == "10":
            import_from_json()
        elif choice == "11":
            import_from_csv()
        elif choice == "12":
            delete_contact()
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    try:
        main_menu()
    except psycopg2.OperationalError as e:
        print("Database connection failed.")
        print("Check that PostgreSQL is running and password is correct.")
        print("Current password in config.py is 12345678.")
        print(e)
        sys.exit(1)
