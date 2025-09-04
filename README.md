(# reconnekt-microservice)

Small utilities and scripts used by the reconnekt microservice project.

## Quick start (macOS / zsh)

1. Create a local virtual environment and activate it

```bash
cd /Users/ud/Workspace/personal/reconnekt-microservice
python3 -m venv .venv
. .venv/bin/activate
```

2. Install runtime dependencies

If the repo contains a `requirements.txt` (recommended):

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If you don't have `requirements.txt`, install the packages used by the scripts:

```bash
python -m pip install --upgrade pip
python -m pip install bcrypt python-dotenv requests
```

3. Provide secrets (Airtable)

Create a `.env` file in the project root with your Airtable values:

```
AIRTABLE_PAT=your_airtable_personal_access_token
AIRTABLE_BASE_ID=appXXXXXXXXXXXX
# optional: AIRTABLE_USER_TABLE=reconnekt_users
```

4. Run the register script (interactive)

```bash
. .venv/bin/activate
python register_user.py
```

The script will prompt for email, password, and initial token count and then attempt to create a user record in the Airtable table configured by the environment variables.

Notes
- The project should not commit the `.venv` directory. `.venv/` is included in `.gitignore`.
- If you prefer a dry run before calling Airtable, open `register_user.py` and replace the `requests.post(...)` call with a `print(data)` for local testing.

