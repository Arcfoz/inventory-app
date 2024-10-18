from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from models.models import Database
from utils.utils import parse_json_body
from config import Config
from handlers.handlers import (
    handle_get_all_categories,
    handle_get_categories,
    handle_get_items,
    handle_get_item,
    handle_create_category,
    handle_login,
    handle_create_item,
    handle_register,
    handle_update_item,
    handle_delete_item,
)

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/categories":
            handle_get_all_categories(self)
        elif url.path == ("/categories/names"):
            handle_get_categories(self)
        elif url.path == ("/items"):
            handle_get_items(self)
        elif url.path.startswith("/items/"):
            item_id = int(url.path.split("/")[-1])
            handle_get_item(self, item_id)
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        url = urlparse(self.path)
        data = parse_json_body(self)

        if url.path == "/categories":
            handle_create_category(self, data)
        elif url.path == "/login":
            handle_login(self, data)
        elif url.path == "/items":
            handle_create_item(self, data)
        elif url.path == "/register":
            handle_register(self, data)
        else:
            self.send_error(404, "Not Found")

    def do_PUT(self):
        url = urlparse(self.path)
        data = parse_json_body(self)

        if url.path.startswith("/items/"):
            item_id = int(url.path.split("/")[-1])
            handle_update_item(self, item_id, data)


    def do_DELETE(self):
        url = urlparse(self.path)

        if url.path.startswith("/items/"):
            item_id = int(url.path.split("/")[-1])
            handle_delete_item(self, item_id)


def run_server():
    server_address = ("", 8000)
    httpd = HTTPServer(server_address, RequestHandler)
    print("Server running on port 8000...")
    httpd.serve_forever()


if __name__ == "__main__":
    db = Database(Config.DATABASE)
    db.close()
    run_server()
