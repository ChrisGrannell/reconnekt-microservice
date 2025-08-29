 # reconnekt_microservice.py
# Flask app to verify JWTs, check token balance from Airtable, and proxy OpenAI requests

from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import bcrypt
import openai
import os
import requests

app = Flask(__name__)
CORS(app)

# Config vars from env
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.environ.get("AIRTABLE_USER_TABLE", "reconnekt_users")
JWT_SECRET = os.environ.get("JWT_SECRET")

openai.api_key = OPENAI_API_KEY

def build_prompt(data):
    name = data.get("name", "")
    company = data.get("company", "")
    linkedin = data.get("linkedin", "")
    met_via = data.get("met_via", "")
    notes = data.get("notes_for_next_time", "")
    output_type = data.get("output_type", "Email")
    historical = data.get("historical_notes", [])

    history = "\n".join([f"- {n['date']}: {n['note']}" for n in historical])

    prompt = f"""You are writing a {output_type} for {name} at {company}.
LinkedIn: {linkedin}
Met via: {met_via}

Notes for next time:
{notes}

Historical notes:
{history}

Respond with only the {output_type.lower()}."""

    if output_type.lower() == "linkedin connection request":
        prompt += "\nIMPORTANT: Must be under 300 characters."
    elif output_type.lower() == "text":
        prompt += "\nIMPORTANT: Keep it ultra short and informal."

    return prompt

def get_airtable_record_by_email(email):
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {"Authorization": f"Bearer {AIRTABLE_PAT}"}
    params = {"filterByFormula": f"{{Username}}='{email}'"}
    response = requests.get(url, headers=headers, params=params)
    records = response.json().get("records", [])
    return records[0] if records else None

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user_record = get_airtable_record_by_email(email)
    if not user_record:
        return jsonify({"error": "User not found"}), 404

    stored_hash = user_record["fields"].get("Password")
    if not bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
        return jsonify({"error": "Invalid password"}), 403

    payload = {"id": user_record["id"], "email": email}
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return jsonify({"token": token})

@app.route("/process-text", methods=["POST"])
def process_text():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Missing token"}), 401

    try:
        token = auth_header.split(" ")[1]
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except Exception as e:
        return jsonify({"error": "Invalid token"}), 403

    user_id = decoded.get("id")

    # Get user record and check tokens
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}/{user_id}"
    headers = {"Authorization": f"Bearer {AIRTABLE_PAT}", "Content-Type": "application/json"}
    record = requests.get(url, headers=headers).json()
    tokens = record.get("fields", {}).get("Tokens", 0)

    if tokens <= 0:
        return jsonify({"error": "Token limit reached"}), 403

    # Build prompt and call OpenAI
    prompt = build_prompt(request.json)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        message = response.choices[0].message.content
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Decrement token count
    requests.patch(url, headers=headers, json={"fields": {"Tokens": tokens - 1}})

    return jsonify({"response": message})

@app.route("/", methods=["GET"])
def health():
    return "✅ Flask server is running"

if __name__ == "__main__":
    app.run(debug=True)

