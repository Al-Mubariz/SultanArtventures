import sqlite3

def init_db():
    conn = sqlite3.connect('db/game.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        levels INTEGER default 0
    )
    ''')


    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized and tables created (if they didn't already exist).")
