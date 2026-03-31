from connect import connect
import csv

def create_table():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS phonebook (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        phone VARCHAR(20)
    )
    """)

    conn.commit()
    conn.close()
    print("Table created!")


def add_contact(name, phone):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO phonebook (name, phone) VALUES (%s, %s)",
        (name, phone)
    )

    conn.commit()
    conn.close()
    print("Contact added!")


def add_contact_from_input():
    name = input("Enter name: ")
    phone = input("Enter phone: ")

    add_contact(name, phone)


def import_from_csv(filename):
    conn = connect()
    cur = conn.cursor()

    with open(filename, newline='') as file:
        reader = csv.reader(file)
        next(reader)  
        for row in reader:
            name, phone = row

            cur.execute(
                "INSERT INTO phonebook (name, phone) VALUES (%s, %s)",
                (name, phone)
            )

    conn.commit()
    conn.close()
    print("CSV imported!")

def update_contact(old_name, new_name=None, new_phone=None):
    conn = connect()
    cur = conn.cursor()

    if new_name:
        cur.execute(
            "UPDATE phonebook SET name = %s WHERE name = %s",
            (new_name, old_name)
        )

    if new_phone:
        cur.execute(
            "UPDATE phonebook SET phone = %s WHERE name = %s",
            (new_phone, old_name)
        )

    conn.commit()
    conn.close()
    print("Contact updated!")

def search_by_name(name):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM phonebook WHERE name ILIKE %s",
        ('%' + name + '%',)
    )

    rows = cur.fetchall()

    for row in rows:
        print(row)

    conn.close()

def search_by_phone_prefix(prefix):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM phonebook WHERE phone LIKE %s",
        (prefix + '%',)
    )

    rows = cur.fetchall()

    for row in rows:
        print(row)

    conn.close()

def delete_contact(value):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM phonebook WHERE name = %s OR phone = %s",
        (value, value)
    )

    conn.commit()
    conn.close()
    print("Contact deleted!")

if __name__ == "__main__":
    # update_contact("Dauren", new_phone="999999")
    # search_by_name("aur")
    # search_by_phone_prefix("+1")
    delete_contact("Dauren")