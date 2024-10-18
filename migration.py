import sqlite3
import argparse
import unittest


class Migration:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def migrate_up(self):
        self.connect()
        try:
            # Read the schema.sql file
            with open("schema.sql", "r") as schema_file:
                schema_script = schema_file.read()

            # Execute the schema script
            self.cursor.executescript(schema_script)

            # Insert dummy data
            self.insert_dummy_data()

            self.conn.commit()
            print("Migration up successful")
        except sqlite3.Error as e:
            print(f"Error migrating up: {e}")
        except IOError as e:
            print(f"Error reading schema.sql file: {e}")
        finally:
            self.close()

    def insert_dummy_data(self):
        # Insert dummy categories
        self.cursor.executemany(
            """
            INSERT INTO categories (name) VALUES (?)
        """,
            [("Electronics",), ("Fashion",), ("Home",)],
        )

        # Insert dummy items
        self.cursor.executemany(
            """
            INSERT INTO items (category_id, name, description, price) VALUES (?, ?, ?, ?)
        """,
            [
                (1, "Laptop", "A high-performance laptop", 999.99),
                (1, "Smartphone", "A smartphone with advanced features", 599.99),
                (2, "T-Shirt", "A high-quality T-shirt", 19.99),
                (2, "Jeans", "A pair of stylish jeans", 49.99),
                (3, "Sofa", "A comfortable sofa", 999.99),
                (3, "Table", "A stylish table", 299.99),
            ],
        )

        # Insert dummy users
        self.cursor.executemany(
            """
            INSERT INTO users (username, password_hash) VALUES (?, ?)
        """,
            [("user1", "password1"), ("user2", "password2")],
        )

    def migrate_down(self):
        self.connect()
        try:
            # Drop all tables
            self.cursor.executescript(
                """
                DROP TABLE IF EXISTS items;
                DROP TABLE IF EXISTS categories;
                DROP TABLE IF EXISTS users;
            """
            )

            self.conn.commit()
            print("Migration down successful")
        except sqlite3.Error as e:
            print(f"Error migrating down: {e}")
        finally:
            self.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migration script")
    subparsers = parser.add_subparsers(dest="action")

    migrate_parser = subparsers.add_parser("migrate", help="Migration actions")
    migrate_parser.add_argument(
        "migration_action", choices=["up", "down"], help="Migration action"
    )

    test_parser = subparsers.add_parser("test", help="Run unit tests")
    test_parser.add_argument("test_file", help="Test file to run")
    test_parser.add_argument(
        "--coverage", action="store_true", help="Run tests with coverage"
    )

    args = parser.parse_args()

    if args.action == "migrate":
        migration = Migration("inventory.db")
        if args.migration_action == "up":
            migration.migrate_up()
        elif args.migration_action == "down":
            migration.migrate_down()
    elif args.action == "test":
        test_file = args.test_file
        if test_file == "tests/testing.py":
            if args.coverage:
                import coverage

                cov = coverage.Coverage()
                cov.start()
                suite = unittest.TestLoader().discover("tests")
                unittest.TextTestRunner().run(suite)
                cov.stop()
                cov.report()
            else:
                suite = unittest.TestLoader().discover("tests")
                unittest.TextTestRunner().run(suite)
        else:
            print("Invalid test file")
