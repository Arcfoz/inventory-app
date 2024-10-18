import unittest
from models.models import Database
from server import RequestHandler
import requests
from config import Config
from http.server import ThreadingHTTPServer
import threading
import utils.utils as utils


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.db = Database(":memory:")  # in-memory database
        self.db.cursor.executescript(
            """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        category_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories (id)
    );
"""
        )

    def tearDown(self):
        self.db.close()

    def test_create_and_get_user(self):
        self.db.create_user("testuser", "password123")
        user = self.db.get_user("testuser")
        self.assertIsNotNone(user)
        self.assertEqual(user[1], "testuser")

    def test_check_password(self):
        self.db.create_user("testuser", "testpassword")
        user = self.db.get_user("testuser")
        self.assertTrue(self.db.check_password(user[2], "testpassword"))
        self.assertFalse(self.db.check_password(user[2], "wrongpassword"))

    def test_create_and_get_categories(self):
        init_categories = self.db.get_categories()

        self.db.create_category(utils.generate_random_char(5))

        categories = self.db.get_categories()

        self.assertEqual(len(categories), len(init_categories) + 1)

    def test_create_and_get_items(self):
        self.db.create_category("Electronics")
        self.db.create_item(1, "Laptop", "A powerful laptop", 1000)
        items = self.db.get_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0][2], "Laptop")
        self.assertEqual(items[0][3], "A powerful laptop")
        self.assertEqual(items[0][4], 1000)

    def test_get_item(self):
        self.db.create_category("Electronics")
        self.db.create_item(1, "Laptop", "A powerful laptop", 999.99)
        item = self.db.get_item(1)
        self.assertIsNotNone(item)
        self.assertEqual(item[2], "Laptop")

    def test_update_item(self):
        self.db.create_category("Electronics")
        self.db.create_item(1, "Laptop", "A powerful laptop", 999.99)
        self.db.update_item(
            1, "Updated Laptop", "An even more powerful laptop", 1099.99
        )
        updated_item = self.db.get_item(1)
        self.assertEqual(updated_item[2], "Updated Laptop")
        self.assertEqual(updated_item[3], "An even more powerful laptop")
        self.assertEqual(updated_item[4], 1099.99)

    def test_delete_item(self):
        self.db.create_category("Electronics")
        self.db.create_item(1, "Laptop", "A powerful laptop", 999.99)
        self.db.delete_item(1)
        items = self.db.get_items()
        self.assertEqual(len(items), 0)


class TestRequestHandler(unittest.TestCase):

    def setUp(self):

        self.server = ThreadingHTTPServer(("localhost", 0), RequestHandler)
        self.port = self.server.server_port
        self.db = Database(Config.DATABASE)

        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

        # Create a test user and get auth token
        self.username = utils.generate_random_char(5)
        self.password = utils.generate_random_char(5)
        self.db.create_user(self.username, self.password)
        self.token = self.get_auth_token()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.db.close()

    def get_auth_token(self):
        login_data = {"username": self.username, "password": self.password}
        response = requests.post(f"http://localhost:{self.port}/login", json=login_data)
        self.assertEqual(response.status_code, 200)
        return response.json()["token"]

    def test_get_categories(self):
        # Get the existing categories
        existing_categories = self.db.get_categories()

        # Create some categories
        self.db.create_category(utils.generate_random_char(5))

        # Send a GET request to /categories
        response = requests.get(f"http://localhost:{self.port}/categories")

        # Check the response
        self.assertEqual(response.status_code, 200)
        categories = response.json()
        self.assertEqual(len(categories), len(existing_categories) + 1)


    def test_get_item(self):
        # Create new category
        self.db.create_category(utils.generate_random_char(5))

        # Get Categories
        len_existing_categories = len(self.db.get_categories())

        # Get the existing test_get_items
        existing_items = self.db.get_items()

        # Create some items
        # category_id, name, description, price
        item_id = self.db.create_item(
            len_existing_categories,
            utils.generate_random_char(5),
            utils.generate_random_char(10),
            utils.generate_random_number(3),
        )

        # Get the existing test_get_item
        existing_item = self.db.get_item(item_id)

        # Send a GET request to /items/1
        response = requests.get(f"http://localhost:{self.port}/items/{item_id}")

        # Check the response
        self.assertEqual(response.status_code, 200)
        item = tuple(response.json().values())
        self.assertEqual(item, existing_item)

    def test_get_item_not_found(self):
        # Send a GET request to /items/1
        response = requests.get(f"http://localhost:{self.port}/items/0")

        # Check the response
        self.assertEqual(response.status_code, 404)

    def test_create_category(self):
        # Get the existing categories
        existing_categories = self.db.get_categories()

        # Create a new category
        category_name = utils.generate_random_char(5)
        data = {"name": category_name}

        # Send a POST request to /categories
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            f"http://localhost:{self.port}/categories", json=data, headers=headers
        )

        # Check the response
        self.assertEqual(response.status_code, 201)
        response_json = response.json()
        self.assertEqual(response_json["message"], "Category created successfully")

        # Check if the category was created in the database
        new_categories = self.db.get_categories()
        self.assertEqual(len(new_categories), len(existing_categories) + 1)

    def test_login(self):
        # Create a new user
        username = utils.generate_random_char(5)
        password = utils.generate_random_char(5)
        self.db.create_user(username, password)

        # Send a POST request to /login
        data = {"username": username, "password": password}

        response = requests.post(f"http://localhost:{self.port}/login", json=data)

        # Check the response
        self.assertEqual(response.status_code, 200)

    def test_create_item(self):
        # Create a new category
        category_name = utils.generate_random_char(5)
        self.db.create_category(category_name)

        # Create a new item
        item_name = utils.generate_random_char(5)
        data = {
            "category_id": 1,
            "name": item_name,
            "description": "Test description",
            "price": 10.99,
        }

        # Send a POST request to /items
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            f"http://localhost:{self.port}/items", json=data, headers=headers
        )

        # Check the response
        self.assertEqual(response.status_code, 201)
        response_json = response.json()
        self.assertEqual(response_json["message"], "Item created")

    def test_update_item(self):
        # Create a new item
        item_name = utils.generate_random_char(5)
        data = {
            "category_id": 1,
            "name": item_name,
            "description": "Test description",
            "price": 10.99,
        }
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            f"http://localhost:{self.port}/items", json=data, headers=headers
        )
        self.assertEqual(response.status_code, 201)

        # Get the item id
        items = self.db.get_items()
        item_id = items[-1][0]

        # Update the item
        new_item_name = utils.generate_random_char(5)
        update_data = {
            "name": new_item_name,
            "description": "New description",
            "price": 20.99,
        }
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.put(
            f"http://localhost:{self.port}/items/{item_id}",
            json=update_data,
            headers=headers,
        )

        # Check the response
        self.assertEqual(response.status_code, 201)
        response_json = response.json()
        self.assertEqual(response_json["message"], "Item Updated")

        # Check if the item was updated in the database
        updated_item = self.db.get_item(item_id)
        self.assertEqual(updated_item[2], new_item_name)
        self.assertEqual(updated_item[3], "New description")
        self.assertEqual(updated_item[4], 20.99)

    def test_delete_item(self):
        # Create a new item
        item_name = utils.generate_random_char(5)
        data = {
            "category_id": 1,
            "name": item_name,
            "description": "Test description",
            "price": 10.99,
        }
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            f"http://localhost:{self.port}/items", json=data, headers=headers
        )
        self.assertEqual(response.status_code, 201)

        # Get the item id
        items = self.db.get_items()
        item_id = items[-1][0]

        # Delete the item
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.delete(
            f"http://localhost:{self.port}/items/{item_id}", headers=headers
        )

        # Check the response
        self.assertEqual(response.status_code, 201)
        response_json = response.json()
        self.assertEqual(response_json["message"], "Item Deleted")

        # Check if the item was deleted from the database
        deleted_item = self.db.get_item(item_id)
        self.assertIsNone(deleted_item)


if __name__ == "__main__":
    unittest.main()
