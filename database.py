import sqlite3

def init_db():
    conn = sqlite3.connect("menu.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dishes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price INTEGER NOT NULL,
            available INTEGER NOT NULL DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()
    print("Database is ready")


def seed_db():
    conn = sqlite3.connect("menu.db")
    cursor = conn.cursor()

    starter_dishes = [
        ("Плов", "main", 40, 1),
        ("Шурпа", "soup", 30, 1),
        ("Самса", "snack", 10, 1),
        ("Чай", "drink", 5, 1),
        ("Кофе", "drink", 15, 0),
    ]

    cursor.executemany(
        "INSERT INTO dishes (name, category, price, available) VALUES (?, ?, ?, ?)",
        starter_dishes
    )

    conn.commit()
    conn.close()
    print(f"{len(starter_dishes)} dishes have been added")


if __name__ == "__main__":
    init_db()
    seed_db()
