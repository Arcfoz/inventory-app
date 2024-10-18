from models.models import Database
from config import Config
from utils.utils import Auth, send_json_response, authenticate
from urllib.parse import urlparse, parse_qs

'''
GET
'''
def handle_get_categories(self):
    db = Database(Config.DATABASE)
    categories = db.get_categories()
    db.close()
    result = []
    for category in categories:
        result.append({
            "id": category[0],
            "name": category[1]
        })
    return send_json_response(self, 200, result)

def handle_get_all_categories(self):
        db = Database(Config.DATABASE)
        categories_with_items = db.get_categories_with_items()
        db.close()
        return send_json_response(self, 200, categories_with_items)

def handle_get_items(self):
    db = Database(Config.DATABASE)
    parsed_url = urlparse(self.path)
    query_params = parse_qs(parsed_url.query)


    page = int(query_params.get('page', [1])[0]) 
    per_page = int(query_params.get('per_page', [10])[0]) 

    
    offset = (page - 1) * per_page

    items = db.get_items(per_page, offset)
    

    total_items = db.get_total_items()
    total_pages = -(-total_items // per_page)

    result = {
        'items': [],
        'pagination': {
            'total_items': total_items,
            'total_pages': total_pages,
            'current_page': page,
        }
    }

    for item in items:
        result['items'].append({
            "id": item[0],
            "category_id": item[1],
            "name": item[2],
            "description": item[3],
            "price": item[4],
            "created_at": item[5],
            "updated_at": item[6]
        })
    db.close()
    return send_json_response(self, 200, result)

def handle_get_item(self, item_id):
    db = Database(Config.DATABASE)
    item = db.get_item(item_id)
    db.close()
    if item is None:
        return send_json_response(self, 404, {"message": "Item not found"})
    result = {
        "id": item[0],
        "category_id": item[1],
        "name": item[2],
        "description": item[3],
        "price": item[4],
        "created_at": item[5],
        "updated_at": item[6]
    }
    return send_json_response(self, 200, result)

'''
POST
'''

def handle_create_category(self, data):
    if not authenticate(self):
        return
    
    db = Database(Config.DATABASE)
    try:
        db.create_category(data['name'])
        db.close()
        return send_json_response(self, 201, {"message": "Category created successfully"})
    except Exception as e:
        db.close()
        return send_json_response(self, 400, {"message": str(e)})

def handle_login(self, data):
    db = Database(Config.DATABASE)
    user = db.get_user(data["username"])
    if user is None or not db.check_password(user[2], data["password"]):
        db.close()
        return send_json_response(self, 401, {"message": "Unauthorized"})
    token = Auth().generate_token()
    db.close()
    return send_json_response(self, 200, {"token": token})

def handle_register(self, data):
    db = Database(Config.DATABASE)
    if not all(key in data for key in ["username", "password"]):
        db.close()
        return send_json_response(self, 400, {"message": "Missing required fields"})

    if db.get_user(data["username"]) is not None:
        db.close()
        return send_json_response(self, 400, {"message": "Username already exists"})

    db.create_user(data["username"], data["password"])
    db.close()
    return send_json_response(self, 201, {"message": "User created successfully"})

def handle_get_items_by_category(self, category_id):
    db = Database(Config.DATABASE)
    items = db.get_items_by_category(category_id)
    db.close()
    if not items:
        return send_json_response(self, 404, {"message": "No items found in this category"})
    return send_json_response(self, 200, items)

def handle_create_item(self, data):
    if not authenticate(self):
        return
    
    db = Database(Config.DATABASE)
    try:
        db.create_item(
            data["category_id"],
            data["name"],
            data.get("description"),
            data["price"],
        )
        db.close()
        return send_json_response(self, 201, {"message": "Item created"})
    except Exception as e:
        db.close()
        return send_json_response(self, 500, {"message": {e}})
    

'''
PUT
'''

def handle_update_item(self, item_id, data):
    if not authenticate(self):
        return
    
    db = Database(Config.DATABASE)
    item = db.get_item(item_id)


    if item is None:
        db.close()
        return send_json_response(self, 404, {"message": "Item not found"})
    
    try:
        db.update_item(
            item[0],
            data["name"],
            data.get("description"),
            data["price"]
        )
        db.close()
        return send_json_response(self, 201, {"message": "Item Updated"})
    except Exception as e:
        db.close()
        return send_json_response(self, 400, {"messagew": str(e)})

'''
DELETE
'''

def handle_delete_item(self, item_id):
    if not authenticate(self):
        return
    
    db = Database(Config.DATABASE)
    item = db.get_item(item_id)


    if item is None:
        db.close()
        return send_json_response(self, 404, {"message": "Item not found"})
    
    try:
        db.delete_item(
            item[0]
        )
        db.close()
        return send_json_response(self, 201, {"message": "Item Deleted"})
    except Exception as e:
        db.close()
        return send_json_response(self, 400, {"messagew": str(e)})