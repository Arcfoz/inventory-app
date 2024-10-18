import base64
import os
import time
import json
import random
import string


class Auth:
    def __init__(self):
        self.secret_key = os.urandom(32)

    def generate_token(self):
        payload = {"exp": int(time.time()) + 3600}  # expires in 1 hour
        token = base64.b64encode(json.dumps(payload).encode()).decode()
        return token

    def verify_token(self, token):
        try:
            payload = json.loads(base64.b64decode(token).decode())
            if payload["exp"] < int(time.time()):
                return False
            return True
        except Exception as e:
            return False

def authenticate(self):
    auth_header = self.headers.get("Authorization")
    if auth_header is None or not auth_header.startswith("Bearer "):
        send_json_response(self, 401, {"message": "Unauthorized"})
        return False
    token = auth_header.split(" ")[1]
    auth = Auth()
    if not auth.verify_token(token):
        send_json_response(self, 401, {"message": "Unauthorized"})
        return False
    return True


def send_json_response(self, status_code, data):
    self.send_response(status_code)
    self.send_header("Content-type", "application/json")
    self.end_headers()
    self.wfile.write(json.dumps(data).encode())


def parse_json_body(self):
    content_length = int(self.headers["Content-Length"])
    body = self.rfile.read(content_length)
    return json.loads(body.decode())


def generate_random_char(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def generate_random_char(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def generate_random_number(length):
    return ''.join(str(random.randint(0, 9)) for _ in range(length))