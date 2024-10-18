import sqlite3
from datetime import datetime
import hashlib
from config import Config


class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def get_user(self, username):
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        return self.cursor.fetchone()

    def check_password(self, hashed_password, password):
        new_hashed_password = hashlib.sha256(
            (password + Config.SECRET_KEY).encode()
        ).hexdigest()
        return new_hashed_password == hashed_password

    def create_user(self, username, password):
        hashed_password = hashlib.sha256(
            (password + Config.SECRET_KEY).encode()
        ).hexdigest()
        self.cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, hashed_password),
        )
        self.conn.commit()

    def get_categories(self):
        self.cursor.execute("SELECT * FROM categories")
        return self.cursor.fetchall()

    def get_categories_with_items(self):
        self.cursor.execute(
            """
            SELECT c.id, c.name
            FROM categories c
        """
        )
        categories = self.cursor.fetchall()
        result = []
        for category in categories:
            self.cursor.execute(
                """
                SELECT i.id, i.name, i.description, i.price
                FROM items i
                WHERE i.category_id = ?
            """,
                (category[0],),
            )
            items = self.cursor.fetchall()
            result.append(
                {
                    "id": category[0],
                    "name": category[1],
                    "items": [
                        {
                            "id": item[0],
                            "name": item[1],
                            "description": item[2],
                            "price": item[3],
                        }
                        for item in items
                    ],
                }
            )
        return result

    def create_category(self, name):
        self.cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        self.conn.commit()
        return self.cursor.lastrowid  # Return the ID of the newly created category

    def get_items(self, limit=10, offset=0):
        self.cursor.execute("SELECT * FROM items LIMIT ? OFFSET ?", (limit, offset))
        return self.cursor.fetchall()

    def get_total_items(self):
        self.cursor.execute("SELECT COUNT(*) FROM items")
        return self.cursor.fetchone()[0]

    def get_item(self, item_id):
        self.cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        return self.cursor.fetchone()

    def create_item(self, category_id, name, description, price):
        if not self.category_exists(category_id):
            raise ValueError("Category does not exist")
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO items (category_id, name, description, price, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (category_id, name, description, price, created_at, updated_at),
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def update_item(self, item_id, name, description, price):
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "UPDATE items SET name = ?, description = ?, price = ?, updated_at =? WHERE id = ?",
            (name, description, price, updated_at, item_id),
        )
        self.conn.commit()

    def delete_item(self, item_id):
        self.cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()

    def category_exists(self, category_id):
        self.cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
        return self.cursor.fetchone() is not None
