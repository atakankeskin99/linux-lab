import os
import time
import secrets
from functools import wraps

from flask import (
    Flask,
    request,
    send_from_directory,
    redirect,
    session,
    abort
)
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024

app.config["SECRET_KEY"] = os.environ.get("LAN_DROP_SECRET")

PIN = os.environ.get("LAN_DROP_PIN")

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 60

failed_login_attempts = {}


def login_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect("/login")

        return function(*args, **kwargs)

    return decorated_function


def get_unique_filename(filename):
    base, extension = os.path.splitext(filename)

    candidate = filename
    counter = 1

    while os.path.exists(
        os.path.join(
            app.config["UPLOAD_FOLDER"],
            candidate
        )
    ):
        candidate = f"{base}_{counter}{extension}"
        counter += 1

    return candidate


def get_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)

    return session["csrf_token"]


def validate_csrf_token():
    session_token = session.get("csrf_token")
    submitted_token = request.form.get("csrf_token")

    if (
        not session_token
        or not submitted_token
        or not secrets.compare_digest(
            session_token,
            submitted_token
        )
    ):
        abort(403)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""

    client_ip = request.remote_addr
    now = time.time()

    login_state = failed_login_attempts.get(
        client_ip,
        {
            "attempts": 0,
            "locked_until": 0
        }
    )

    if login_state["locked_until"] > now:
        remaining_seconds = int(
            login_state["locked_until"] - now
        ) + 1

        error = (
            f"Too many incorrect attempts. "
            f"Try again in {remaining_seconds} seconds."
        )

    elif request.method == "POST":
        entered_pin = request.form.get("pin", "")

        if PIN and entered_pin == PIN:
            failed_login_attempts.pop(client_ip, None)

            session.clear()
            session["authenticated"] = True
            session["csrf_token"] = secrets.token_urlsafe(32)

            return redirect("/")

        login_state["attempts"] += 1

        if login_state["attempts"] >= MAX_LOGIN_ATTEMPTS:
            login_state["attempts"] = 0
            login_state["locked_until"] = (
                now + LOCKOUT_SECONDS
            )

            error = (
                "Too many incorrect attempts. "
                f"Try again in {LOCKOUT_SECONDS} seconds."
            )

        else:
            remaining_attempts = (
                MAX_LOGIN_ATTEMPTS
                - login_state["attempts"]
            )

            error = (
                "Incorrect PIN. "
                f"{remaining_attempts} attempts remaining."
            )

        failed_login_attempts[client_ip] = login_state

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>LAN Drop</title>

    <style>
        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            color: #1f2937;
        }}

        .container {{
            width: min(92%, 420px);
            margin: 100px auto;
        }}

        .card {{
            background: white;
            padding: 30px;
            border-radius: 14px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
            text-align: center;
        }}

        h1 {{
            margin-top: 0;
        }}

        .subtitle {{
            color: #6b7280;
        }}

        input {{
            width: 100%;
            padding: 14px;
            margin: 18px 0 12px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            text-align: center;
            font-size: 20px;
            letter-spacing: 6px;
        }}

        button {{
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 8px;
            background: #111827;
            color: white;
            font-size: 15px;
            cursor: pointer;
        }}

        .error {{
            color: #dc2626;
        }}
    </style>
</head>

<body>
    <div class="container">
        <div class="card">
            <h1>LAN Drop</h1>

            <p class="subtitle">
                Enter the 6-digit PIN to continue.
            </p>

            <form method="POST">
                <input
                    type="password"
                    name="pin"
                    inputmode="numeric"
                    pattern="[0-9]{{6}}"
                    maxlength="6"
                    placeholder="••••••"
                    required
                >

                <button type="submit">
                    Unlock
                </button>
            </form>

            <p class="error">{error}</p>
        </div>
    </div>
</body>
</html>
"""


@app.route("/")
@login_required
def home():
    files = os.listdir(UPLOAD_FOLDER)
    csrf_token = get_csrf_token()

    file_list = ""

    for filename in files:
        file_list += f"""
        <li class="file-row">
            <span class="filename">{filename}</span>

            <div class="actions">
                <a class="download-btn" href="/download/{filename}">
                    Download
                </a>

                <form
                    class="delete-form"
                    action="/delete/{filename}"
                    method="POST"
                >
                    <input
                        type="hidden"
                        name="csrf_token"
                        value="{csrf_token}"
                    >

                    <button class="delete-btn" type="submit">
                        Delete
                    </button>
                </form>
            </div>
        </li>
        """

    if files:
        files_html = f"<ul>{file_list}</ul>"
    else:
        files_html = '<p class="empty">No files uploaded yet.</p>'

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>LAN Drop</title>

    <style>
        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            color: #1f2937;
        }}

        .container {{
            width: min(92%, 650px);
            margin: 60px auto;
        }}

        .card {{
            background: white;
            padding: 28px;
            border-radius: 14px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
        }}

        h1 {{
            margin-top: 0;
            margin-bottom: 8px;
        }}

        h2 {{
            margin-top: 30px;
        }}

        .subtitle {{
            margin-top: 0;
            color: #6b7280;
        }}

        .upload-form {{
            margin: 28px 0;
            padding: 20px;
            border: 2px dashed #cbd5e1;
            border-radius: 10px;
        }}

        input[type="file"] {{
            width: 100%;
            margin-bottom: 14px;
        }}

        .upload-btn {{
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 8px;
            background: #111827;
            color: white;
            font-size: 15px;
            cursor: pointer;
        }}

        ul {{
            list-style: none;
            padding: 0;
        }}

        .file-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 14px;
            padding: 12px;
            margin-bottom: 8px;
            background: #f8fafc;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
        }}

        .filename {{
            overflow-wrap: anywhere;
        }}

        .actions {{
            display: flex;
            gap: 8px;
            flex-shrink: 0;
        }}

        .download-btn,
        .delete-btn {{
            display: inline-block;
            padding: 8px 10px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            text-decoration: none;
            cursor: pointer;
        }}

        .download-btn {{
            background: #2563eb;
            color: white;
        }}

        .delete-btn {{
            background: #dc2626;
            color: white;
        }}

        .delete-form {{
            margin: 0;
        }}

        .empty {{
            color: #6b7280;
        }}

        @media (max-width: 500px) {{
            .file-row {{
                align-items: stretch;
                flex-direction: column;
            }}

            .actions {{
                width: 100%;
            }}

            .download-btn,
            .delete-btn {{
                flex: 1;
                text-align: center;
            }}

            .delete-form {{
                flex: 1;
            }}

            .delete-btn {{
                width: 100%;
            }}
        }}
    </style>
</head>

<body>
    <div class="container">
        <div class="card">
            <h1>LAN Drop</h1>

            <p class="subtitle">
                Simple file transfer over your local network.
            </p>

            <form
                class="upload-form"
                action="/upload"
                method="POST"
                enctype="multipart/form-data"
            >
                <input
                    type="hidden"
                    name="csrf_token"
                    value="{csrf_token}"
                >

                <input type="file" name="file" multiple required>

                <button class="upload-btn" type="submit">
                    Upload file
                </button>
            </form>

            <h2>Available files</h2>

            {files_html}
        </div>
    </div>
</body>
</html>
"""


@app.route("/upload", methods=["POST"])
@login_required
def upload():
    validate_csrf_token()

    files = request.files.getlist("file")

    for file in files:
        if not file.filename:
            continue

        filename = secure_filename(file.filename)

        if not filename:
            continue

        filename = get_unique_filename(filename)

        file.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )
        )

    return redirect("/")


@app.route("/download/<filename>")
@login_required
def download(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename,
        as_attachment=True
    )


@app.route("/delete/<filename>", methods=["POST"])
@login_required
def delete(filename):
    validate_csrf_token()

    safe_filename = secure_filename(filename)

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        safe_filename
    )

    if os.path.exists(file_path):
        os.remove(file_path)

    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    if not app.config["SECRET_KEY"]:
        raise RuntimeError(
            "LAN_DROP_SECRET environment variable is not set."
        )

    if not PIN:
        raise RuntimeError(
            "LAN_DROP_PIN environment variable is not set."
        )

    if not PIN.isdigit() or len(PIN) != 6:
        raise RuntimeError(
            "LAN_DROP_PIN must contain exactly 6 digits."
        )

    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False,
        use_reloader=False,
        ssl_context=(
            "lan-drop.pem",
            "lan-drop-key.pem"
        )
    )
