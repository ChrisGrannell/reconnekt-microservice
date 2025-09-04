# register_user.py
# Script to create users in Airtable with bcrypt-hashed passwords, using Airtable Personal Access Token

import bcrypt
import requests
import os
from dotenv import load_dotenv

load_dotenv()

AIRTABLE_PAT = os.environ.get("AIRTABLE_PAT")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.environ.get("AIRTABLE_USER_TABLE", "reconnekt_users")

if not AIRTABLE_PAT:
    raise ValueError("Missing AIRTABLE_PAT in .env")
if not AIRTABLE_BASE_ID:
    raise ValueError("Missing AIRTABLE_BASE_ID in .env")

AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_PAT}",
    "Content-Type": "application/json"
}

def create_user(email, plain_password, initial_tokens):
    hashed_password = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    data = {
        "fields": {
            "username": email,
            "password": hashed_password,
            "tokens": initial_tokens
        }
    }

    response = requests.post(AIRTABLE_URL, json=data, headers=HEADERS)
    if response.status_code == 200:
        print(f"✅ User {email} added successfully.")
    else:
        print(f"❌ Failed to add user: {response.status_code} {response.text}")
        if response.status_code == 404:
            print("🔍 Check your AIRTABLE_BASE_ID and AIRTABLE_USER_TABLE values.")
        elif response.status_code == 401:
            print("🔒 Invalid or expired AIRTABLE_PAT. Go to https://airtable.com/create/tokens to generate a new one.")

if __name__ == "__main__":
    email = input("Enter user email: ").strip()
    password = input("Enter user password: ").strip()
    tokens = int(input("Initial token count: "))

    create_user(email, password, tokens)
