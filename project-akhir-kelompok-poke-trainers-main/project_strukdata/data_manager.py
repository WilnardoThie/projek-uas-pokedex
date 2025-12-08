import json
import os
import bcrypt 

USER_FILE = 'users.json'
ENCODING = 'utf-8'

def _load_users():
    if not os.path.exists(USER_FILE):
        return {}
    try:
        with open(USER_FILE, 'r', encoding=ENCODING) as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def _save_users(users_data):
    with open(USER_FILE, 'w', encoding=ENCODING) as f:
        json.dump(users_data, f, indent=4)

def register_user(email, password, username):
    users = _load_users()
    
    if email in users:
        return False
        
    password_bytes = password.encode(ENCODING)
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12))
    
    users[email] = {
        "username": username,
        "password": hashed_password.decode(ENCODING), 
        "profile": {"Nama": username, "Email": email, "Deskripsi": ""},
        "saved_deck": [],
        "saved_teams": {},
        "search_history": [] 
    }
    
    _save_users(users)
    return True

def authenticate_user(email, password):
    users = _load_users()
    user_data = users.get(email)
    
    if not user_data:
        return None
    
    stored_hash = user_data.get("password", "").encode(ENCODING)
    
    if bcrypt.checkpw(password.encode(ENCODING), stored_hash):
        return user_data
    else:
        return None

def get_user_email_by_username(username):
    users = _load_users()
    for email, user_data in users.items():
        if user_data.get("username", "").lower() == username.lower():
            return email
    return None

def get_user_data(email):
    users = _load_users()
    user_data = users.get(email)
    if user_data:
        if 'saved_deck' not in user_data:
            user_data['saved_deck'] = []
        if 'saved_teams' not in user_data:
            user_data['saved_teams'] = {}
        if 'search_history' not in user_data: 
            user_data['search_history'] = []
    return user_data


def save_user_profile(email, data_to_save):
    users = _load_users()
    if email in users:
        current_profile = users[email].get("profile", {})
        
        if 'profile' in data_to_save:
             users[email]["profile"] = {
                "Nama": data_to_save["profile"].get("Nama", current_profile.get("Nama")),
                "Email": data_to_save["profile"].get("Email", current_profile.get("Email")),
                "Deskripsi": data_to_save["profile"].get("Deskripsi", current_profile.get("Deskripsi"))
            }
             users[email]["username"] = users[email]["profile"]["Nama"]

        if 'saved_deck' in data_to_save:
            users[email]["saved_deck"] = data_to_save['saved_deck']

        if 'saved_teams' in data_to_save:
            users[email]["saved_teams"] = data_to_save['saved_teams']
        
        if 'search_history' in data_to_save: 
            users[email]["search_history"] = data_to_save['search_history']

        _save_users(users)
        return True
    return False
