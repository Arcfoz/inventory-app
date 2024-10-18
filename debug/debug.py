class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        url = urlparse(self.path)
        if url.path == "/items":
            auth_header = self.headers.get("Authorization")
            if auth_header is None or not auth_header.startswith("Bearer "):
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"message": "Unauthorized"}).encode())
                return
            token = auth_header.split(" ")[1]
            auth = Auth()
            if not auth.verify_token(token):
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"message": "Unauthorized"}).encode())
                return
            content_length = int(self.headers["Content-Length"])
            body = self.rfile.read(content_length)
            data = json.loads(body.decode())
            db = Database(Config.DATABASE)
            db.create_item(
                data["category_id"],
                data["name"],
                data.get("description"),
                data["price"],
            )
            db.close()
            self.send_response(201)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Item created"}).encode())