import os
import json
import base64
import time
import asyncio
import requests
import sqlite3
import datetime
import random
import string
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

TOKEN    = os.environ.get("TELEGRAM_BOT_TOKEN")
ADMINS   = [8546348748, 8737475340]
ADMIN_USERNAME = "@happy_gamer2"

# GitHub Configuration
GITHUB_TOKEN = (os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or "").strip()
GITHUB_REPO  = (os.environ.get("GH_REPO") or os.environ.get("GITHUB_REPO") or "sagarhalder7865-hub/my-telegram-bot").strip()
DATA_FILE    = "bot_data.json"

# Gist Config
GIST_ID   = "e155b8f93a7476556fa1c8b2dfc9b164"
FILE_NAME = "status.txt"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "bot_data.db")
QR_PATH  = os.path.join(BASE_DIR, "payment_qr.png")

# --- 24/7 ULTRA CLOUD WEB SERVER ---
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        html = """
        <html>
        <head><title>Happy Gamer VIP Cloud</title></head>
        <body style="background:#0b0e14;color:#00e5ff;font-family:sans-serif;text-align:center;padding-top:50px;">
            <h1>👑 HAPPY GAMER VIP BOT ENGINE</h1>
            <p style="color:#00ff66;">⚡ Status: Running 24/7 Fast Engine</p>
        </body>
        </html>
        """
        self.wfile.write(html.encode("utf-8"))
    def log_message(self, format, *args):
        return

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

Thread(target=run_web_server, daemon=True).start()

# --- SCRIPT KEY PRICES ---
SCRIPT_PRICES = {
    1: 20,
    3: 40,
    7: 80,
    15: 150,
    30: 200,
    90: 500
}

# --- DEFAULT PRICING CATALOG ---
DEFAULT_PRICES = {
    # 👑 Shinigami Auto Play
    "shini_1d": {"game": "Shinigami", "label": "1 Day", "reg": 70, "res": 65},
    "shini_3d": {"game": "Shinigami", "label": "3 Days", "reg": 160, "res": 150},
    "shini_7d": {"game": "Shinigami", "label": "7 Days", "reg": 250, "res": 230},
    "shini_15d": {"game": "Shinigami", "label": "15 Days", "reg": 360, "res": 340},
    "shini_30d": {"game": "Shinigami", "label": "30 Days", "reg": 560, "res": 530},

    # 🍏 Lynx iOS
    "lynx_ios_1d": {"game": "Lynx iOS", "label": "1 Day", "reg": 320, "res": 300},
    "lynx_ios_3d": {"game": "Lynx iOS", "label": "3 Days", "reg": 560, "res": 530},
    "lynx_ios_7d": {"game": "Lynx iOS", "label": "7 Days", "reg": 820, "res": 780},
    "lynx_ios_15d": {"game": "Lynx iOS", "label": "15 Days", "reg": 1370, "res": 1300},
    "lynx_ios_30d": {"game": "Lynx iOS", "label": "30 Days", "reg": 2200, "res": 2100},

    # 🤖 Lynx Android
    "lynx_and_1d": {"game": "Lynx Android", "label": "1 Day", "reg": 140, "res": 130},
    "lynx_and_3d": {"game": "Lynx Android", "label": "3 Days", "reg": 230, "res": 210},
    "lynx_and_7d": {"game": "Lynx Android", "label": "7 Days", "reg": 460, "res": 430},
    "lynx_and_15d": {"game": "Lynx Android", "label": "15 Days", "reg": 560, "res": 530},
    "lynx_and_30d": {"game": "Lynx Android", "label": "30 Days", "reg": 1200, "res": 1150},

    # 👿 AIM-AI CARROM ENGINE
    "aim_1d":  {"game": "AIM-AI Carrom", "label": "01 Day",  "reg": 70,   "res": 65},
    "aim_3d":  {"game": "AIM-AI Carrom", "label": "03 Days", "reg": 140,  "res": 130},
    "aim_7d":  {"game": "AIM-AI Carrom", "label": "07 Days", "reg": 240,  "res": 220},
    "aim_15d": {"game": "AIM-AI Carrom", "label": "15 Days", "reg": 360,  "res": 340},
    "aim_30d": {"game": "AIM-AI Carrom", "label": "30 Days", "reg": 650,  "res": 600},
    "aim_90d": {"game": "AIM-AI Carrom", "label": "90 Days", "reg": 1700, "res": 1600},

    # 👑 AIM CARROM KING
    "acn_3d":  {"game": "AIM Normal", "label": "3 Days",  "reg": 100, "res": 80},
    "acn_7d":  {"game": "AIM Normal", "label": "1 Week",  "reg": 180, "res": 150},
    "acn_30d": {"game": "AIM Normal", "label": "1 Month", "reg": 490, "res": 420},
    "acp_3d":  {"game": "AIM Premium", "label": "3 Days", "reg": 120, "res": 100},
    "acp_7d":  {"game": "AIM Premium", "label": "1 Week", "reg": 200, "res": 170},
    "acp_30d": {"game": "AIM Premium", "label": "1 Month","reg": 570, "res": 500},

    # 🔥 KOS ENGINE
    "b1":  {"game": "KOS 8 Ball", "label": "1 Day",   "reg": 120, "res": 100},
    "b7":  {"game": "KOS 8 Ball", "label": "7 Days",  "reg": 260, "res": 230},
    "b15": {"game": "KOS 8 Ball", "label": "15 Days", "reg": 480, "res": 420},
    "b30": {"game": "KOS 8 Ball", "label": "30 Days", "reg": 780, "res": 700},

    "c1":  {"game": "KOS Carrom", "label": "1 Day",   "reg": 100, "res": 90},
    "c7":  {"game": "KOS Carrom", "label": "7 Days",  "reg": 250, "res": 220},
    "c15": {"game": "KOS Carrom", "label": "15 Days", "reg": 430, "res": 390},
    "c30": {"game": "KOS Carrom", "label": "30 Days", "reg": 730, "res": 680},

    "f1":  {"game": "KOS FreeFire", "label": "1 Day",  "reg": 120, "res": 100},
    "f7":  {"game": "KOS FreeFire", "label": "7 Days", "reg": 300, "res": 260},
    "f30": {"game": "KOS FreeFire", "label": "30 Days","reg": 830, "res": 750},

    # ⚡ BITAIM
    "bit7":  {"game": "Bitaim", "label": "7 Days",    "reg": 200,  "res": 170},
    "bit30": {"game": "Bitaim", "label": "30 Days",   "reg": 500,  "res": 430},
    "bit90": {"game": "Bitaim", "label": "90 Days",   "reg": 800,  "res": 700},
    "bitlt": {"game": "Bitaim", "label": "Lifetime",  "reg": 2000, "res": 1700},

    # 🐍 SNAKE ENGINE
    "snkc_3d":  {"game": "Snake Carrom", "label": "3 Days",  "reg": 200, "res": 170},
    "snkc_10d": {"game": "Snake Carrom", "label": "10 Days", "reg": 580, "res": 520},
    "snkc_30d": {"game": "Snake Carrom", "label": "30 Days", "reg": 2100,"res": 1900},
    "snk8_3d":  {"game": "Snake 8 Ball", "label": "3 Days",  "reg": 200, "res": 170},
    "snk8_10d": {"game": "Snake 8 Ball", "label": "10 Days", "reg": 560, "res": 500},
    "snk8_30d": {"game": "Snake 8 Ball", "label": "30 Days", "reg": 2100,"res": 1900}
}

def get_auth_headers():
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "HappyGamerBot"
    }

def generate_short_key(name="", is_main=True):
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    if is_main:
        prefix = "HG"
    else:
        clean_name = ''.join(c for c in name if c.isalpha()).upper()
        prefix = clean_name[:3] if len(clean_name) >= 3 else (clean_name + "VIP")[:3]
    return f"{prefix}{random_chars}"

def clean_expired_lines(content_text):
    lines = content_text.splitlines()
    today_int = int(datetime.datetime.now().strftime("%Y%m%d"))
    cleaned_lines = []
    removed_count = 0
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        
        if line_clean.startswith("HGTOKEN=") or line_clean.startswith("HGTOKEN=="):
            parts = [p for p in line_clean.split("=") if p != ""]
            exp_date_str = None
            for p in parts:
                if len(p) == 8 and p.isdigit():
                    exp_date_str = p
                    break
            
            if exp_date_str:
                try:
                    exp_date_int = int(exp_date_str)
                    if exp_date_int < today_int:
                        removed_count += 1
                        continue
                except Exception:
                    pass
        cleaned_lines.append(line_clean)
        
    return "\n".join(cleaned_lines), removed_count

def append_to_gist(vip_key, device_id, days):
    try:
        if not GITHUB_TOKEN:
            return False, None, "Server Token is not set in Environment!"

        expiry = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y%m%d")
        new_entry = f"HGTOKEN={vip_key}={expiry}={device_id}"
        
        headers = get_auth_headers()
        get_url = f"https://api.github.com/gists/{GIST_ID}"
        
        get_res = requests.get(get_url, headers=headers, timeout=10)
        current_content = ""
        if get_res.status_code == 200:
            files_data = get_res.json().get("files", {})
            if FILE_NAME in files_data:
                current_content = files_data[FILE_NAME].get("content", "")
        else:
            raw_url = f"https://gist.githubusercontent.com/sagarhalder7865-hub/{GIST_ID}/raw/{FILE_NAME}?t={int(time.time())}"
            raw_res = requests.get(raw_url, timeout=10)
            if raw_res.status_code == 200:
                current_content = raw_res.text

        filtered_content, removed = clean_expired_lines(current_content)

        if filtered_content:
            updated_content = filtered_content.strip() + "\n" + new_entry
        else:
            updated_content = "STATUS=ON\n" + new_entry

        patch_payload = {"files": {FILE_NAME: {"content": updated_content}}}
        patch_res = requests.patch(get_url, headers=headers, json=patch_payload, timeout=10)
        
        if patch_res.status_code in [200, 201]:
            return True, expiry, None
        else:
            err_details = patch_res.json().get("message", patch_res.text)
            return False, None, f"Status {patch_res.status_code}: {err_details}"
    except Exception as e:
        return False, None, str(e)

def purge_expired_gist_keys():
    try:
        if not GITHUB_TOKEN: return 0
        headers = get_auth_headers()
        get_url = f"https://api.github.com/gists/{GIST_ID}"
        get_res = requests.get(get_url, headers=headers, timeout=10)
        if get_res.status_code != 200: return 0
        
        files_data = get_res.json().get("files", {})
        if FILE_NAME not in files_data: return 0
            
        current_content = files_data[FILE_NAME].get("content", "")
        cleaned_content, removed = clean_expired_lines(current_content)
        
        if removed > 0:
            patch_payload = {"files": {FILE_NAME: {"content": cleaned_content}}}
            requests.patch(get_url, headers=headers, json=patch_payload, timeout=10)
        return removed
    except Exception as e:
        return 0

def remove_device_from_gist(device_id):
    if not GITHUB_TOKEN:
        return False, 0, "Server Token is not set in Environment!"
    try:
        headers = get_auth_headers()
        get_url = f"https://api.github.com/gists/{GIST_ID}"
        get_res = requests.get(get_url, headers=headers, timeout=10)
        current_content = ""
        if get_res.status_code == 200:
            files_data = get_res.json().get("files", {})
            if FILE_NAME in files_data:
                current_content = files_data[FILE_NAME].get("content", "")
        else:
            raw_url = f"https://gist.githubusercontent.com/sagarhalder7865-hub/{GIST_ID}/raw/{FILE_NAME}?t={int(time.time())}"
            raw_res = requests.get(raw_url, timeout=10)
            if raw_res.status_code == 200:
                current_content = raw_res.text

        lines = current_content.splitlines()
        new_lines = []
        removed_count = 0
        for line in lines:
            if line.strip() and device_id in line:
                removed_count += 1
            else:
                if line.strip():
                    new_lines.append(line.strip())

        if removed_count == 0:
            return False, 0, "Device ID not found in active cloud keys!"

        updated_content = "\n".join(new_lines)
        patch_payload = {"files": {FILE_NAME: {"content": updated_content}}}
        patch_res = requests.patch(get_url, headers=headers, json=patch_payload, timeout=10)
        if patch_res.status_code in [200, 201]:
            return True, removed_count, None
        else:
            err_details = patch_res.json().get("message", patch_res.text)
            return False, removed_count, f"Status {patch_res.status_code}: {err_details}"
    except Exception as e:
        return False, 0, str(e)

# --- ASYNC NON-BLOCKING GITHUB SYNC ENGINE ---
def push_data_to_github_bg():
    Thread(target=push_data_to_github, daemon=True).start()

def push_data_to_github():
    if not GITHUB_TOKEN or not GITHUB_REPO: return
    try:
        data_dump = export_database_json()
        content_str = json.dumps(data_dump, indent=2)
        content_b64 = base64.b64encode(content_str.encode("utf-8")).decode("utf-8")
        
        headers = get_auth_headers()
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{DATA_FILE}"
        
        get_res = requests.get(url, headers=headers, timeout=8)
        payload = {
            "message": f"Cloud Sync: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "content": content_b64
        }
        if get_res.status_code == 200:
            payload["sha"] = get_res.json().get("sha")
            
        requests.put(url, headers=headers, json=payload, timeout=8)
    except Exception:
        pass

def pull_data_from_github():
    if not GITHUB_TOKEN or not GITHUB_REPO: return None
    try:
        headers = get_auth_headers()
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{DATA_FILE}"
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            content_b64 = res.json().get("content", "")
            content_str = base64.b64decode(content_b64).decode("utf-8")
            return json.loads(content_str)
    except Exception:
        pass
    return None

def export_database_json():
    with get_db() as db:
        users = [dict(r) for r in db.execute("SELECT * FROM users").fetchall()]
        keys = [dict(r) for r in db.execute("SELECT * FROM keys").fetchall()]
        orders = [dict(r) for r in db.execute("SELECT * FROM order_history").fetchall()]
        resellers = [dict(r) for r in db.execute("SELECT * FROM resellers").fetchall()]
        prices = [dict(r) for r in db.execute("SELECT * FROM prices").fetchall()]
        script_admins = [dict(r) for r in db.execute("SELECT * FROM script_admins").fetchall()]
        return {
            "users": users, "keys": keys, "orders": orders,
            "resellers": resellers, "prices": prices, "script_admins": script_admins
        }

# --- DATABASE SETUP ---
def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=15)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(force_fresh=False):
    if force_fresh and os.path.exists(DB_PATH):
        try: os.remove(DB_PATH)
        except Exception: pass

    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                username TEXT,
                balance INTEGER DEFAULT 0,
                script_balance INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0,
                referrer_id INTEGER DEFAULT 0,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        try:
            db.execute("ALTER TABLE users ADD COLUMN script_balance INTEGER DEFAULT 0")
        except Exception: pass
        
        db.execute("""
            CREATE TABLE IF NOT EXISTS script_admins (
                user_id INTEGER PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan TEXT,
                key_code TEXT UNIQUE,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS order_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                game TEXT,
                plan_label TEXT,
                price INTEGER,
                key_delivered TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS resellers (
                user_id INTEGER PRIMARY KEY
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS prices (
                plan_id TEXT PRIMARY KEY,
                game TEXT,
                label TEXT,
                regular INTEGER,
                reseller INTEGER
            )
        """)

        # Sync Default Prices
        for plan_id, d in DEFAULT_PRICES.items():
            db.execute(
                "INSERT INTO prices (plan_id, game, label, regular, reseller) VALUES (?,?,?,?,?) "
                "ON CONFLICT(plan_id) DO UPDATE SET regular=excluded.regular, reseller=excluded.reseller",
                (plan_id, d["game"], d["label"], d["reg"], d["res"])
            )

    if not force_fresh:
        gh_data = pull_data_from_github()
        if gh_data:
            with get_db() as db:
                for u in gh_data.get("users", []):
                    db.execute(
                        "INSERT OR REPLACE INTO users (user_id, first_name, username, balance, script_balance, is_banned, referrer_id, joined_at) "
                        "VALUES (?,?,?,?,?,?,?,?)",
                        (u["user_id"], u.get("first_name",""), u.get("username",""), u.get("balance",0), u.get("script_balance",0), u.get("is_banned",0), u.get("referrer_id",0), u.get("joined_at",""))
                    )
                for sa in gh_data.get("script_admins", []):
                    db.execute("INSERT OR IGNORE INTO script_admins (user_id) VALUES (?)", (sa["user_id"],))
                for k in gh_data.get("keys", []):
                    db.execute("INSERT OR IGNORE INTO keys (plan, key_code) VALUES (?,?)", (k["plan"], k["key_code"]))
                for r in gh_data.get("resellers", []):
                    db.execute("INSERT OR IGNORE INTO resellers (user_id) VALUES (?)", (r["user_id"],))
                for o in gh_data.get("orders", []):
                    db.execute(
                        "INSERT OR IGNORE INTO order_history (id, user_id, game, plan_label, price, key_delivered, timestamp) VALUES (?,?,?,?,?,?,?)",
                        (o["id"], o["user_id"], o["game"], o["plan_label"], o["price"], o["key_delivered"], o["timestamp"])
                    )

init_db()

# Database Helper Methods
def db_is_banned(user_id):
    with get_db() as db:
        r = db.execute("SELECT is_banned FROM users WHERE user_id=?", (user_id,)).fetchone()
        return bool(r and r["is_banned"])

def db_ban_user(user_id, reason="Blacklisted"):
    with get_db() as db:
        db.execute("UPDATE users SET is_banned=1 WHERE user_id=?", (user_id,))
    push_data_to_github_bg()

def db_unban_user(user_id):
    with get_db() as db:
        db.execute("UPDATE users SET is_banned=0 WHERE user_id=?", (user_id,))
    push_data_to_github_bg()

def db_register_user(user_id, first_name, username, referrer_id=0):
    with get_db() as db:
        row = db.execute("SELECT user_id, referrer_id FROM users WHERE user_id=?", (user_id,)).fetchone()
        if not row:
            ref_giver = None
            if referrer_id and referrer_id != user_id:
                chk = db.execute("SELECT user_id FROM users WHERE user_id=?", (referrer_id,)).fetchone()
                if chk:
                    ref_giver = referrer_id
                    db.execute("UPDATE users SET balance = balance + 1 WHERE user_id=?", (referrer_id,))
            db.execute(
                "INSERT INTO users (user_id, first_name, username, balance, referrer_id) VALUES (?,?,?,?,?)",
                (user_id, first_name, username, 0, ref_giver or 0)
            )
            push_data_to_github_bg()
            return ref_giver
        else:
            db.execute("UPDATE users SET first_name=?, username=? WHERE user_id=?", (first_name, username, user_id))
    return None

def db_get_referral_count(user_id):
    with get_db() as db:
        r = db.execute("SELECT COUNT(*) as c FROM users WHERE referrer_id=?", (user_id,)).fetchone()
        return r["c"] if r else 0

def db_get_all_users():
    with get_db() as db:
        return [r["user_id"] for r in db.execute("SELECT user_id FROM users").fetchall()]

def db_get_balance(user_id):
    with get_db() as db:
        r = db.execute("SELECT balance FROM users WHERE user_id=?", (user_id,)).fetchone()
        return r["balance"] if r else 0

def db_set_balance(user_id, amount):
    with get_db() as db:
        db.execute(
            "INSERT INTO users (user_id, balance) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET balance = excluded.balance",
            (user_id, amount)
        )
    push_data_to_github_bg()

def db_add_balance(user_id, delta):
    with get_db() as db:
        db.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (delta, user_id))
        r = db.execute("SELECT balance FROM users WHERE user_id=?", (user_id,)).fetchone()
    push_data_to_github_bg()
    return r["balance"] if r else 0

def db_get_script_balance(user_id):
    with get_db() as db:
        r = db.execute("SELECT script_balance FROM users WHERE user_id=?", (user_id,)).fetchone()
        return r["script_balance"] if r and r["script_balance"] is not None else 0

def db_set_script_balance(user_id, amount):
    with get_db() as db:
        db.execute(
            "INSERT INTO users (user_id, script_balance) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET script_balance = excluded.script_balance",
            (user_id, amount)
        )
    push_data_to_github_bg()

def db_add_script_balance(user_id, delta):
    with get_db() as db:
        db.execute("UPDATE users SET script_balance = COALESCE(script_balance, 0) + ? WHERE user_id=?", (delta, user_id))
        r = db.execute("SELECT script_balance FROM users WHERE user_id=?", (user_id,)).fetchone()
    push_data_to_github_bg()
    return r["script_balance"] if r else 0

def db_count_keys(plan):
    with get_db() as db:
        r = db.execute("SELECT COUNT(*) as c FROM keys WHERE plan=?", (plan,)).fetchone()
        return r["c"] if r else 0

def db_add_key(plan, key):
    with get_db() as db:
        db.execute("INSERT OR IGNORE INTO keys (plan, key_code) VALUES (?,?)", (plan, key.strip()))
    push_data_to_github_bg()

def db_pop_key(plan):
    with get_db() as db:
        r = db.execute("SELECT id, key_code FROM keys WHERE plan=? LIMIT 1", (plan,)).fetchone()
        if r:
            db.execute("DELETE FROM keys WHERE id=?", (r["id"],))
            push_data_to_github_bg()
            return r["key_code"]
    return None

def db_is_reseller(user_id):
    with get_db() as db:
        return bool(db.execute("SELECT 1 FROM resellers WHERE user_id=?", (user_id,)).fetchone())

def db_add_reseller(user_id):
    with get_db() as db:
        db.execute("INSERT OR IGNORE INTO resellers (user_id) VALUES (?)", (user_id,))
    push_data_to_github_bg()

def db_remove_reseller(user_id):
    with get_db() as db:
        db.execute("DELETE FROM resellers WHERE user_id=?", (user_id,))
    push_data_to_github_bg()

def db_all_resellers():
    with get_db() as db:
        return [r["user_id"] for r in db.execute("SELECT user_id FROM resellers").fetchall()]

def db_is_script_admin(user_id):
    with get_db() as db:
        return bool(db.execute("SELECT 1 FROM script_admins WHERE user_id=?", (user_id,)).fetchone())

def db_add_script_admin(user_id):
    with get_db() as db:
        db.execute("INSERT OR IGNORE INTO script_admins (user_id) VALUES (?)", (user_id,))
    push_data_to_github_bg()

def db_remove_script_admin(user_id):
    with get_db() as db:
        db.execute("DELETE FROM script_admins WHERE user_id=?", (user_id,))
    push_data_to_github_bg()

def db_all_script_admins():
    with get_db() as db:
        return [r["user_id"] for r in db.execute("SELECT user_id FROM script_admins").fetchall()]

def db_get_plan(plan_id):
    with get_db() as db:
        r = db.execute("SELECT * FROM prices WHERE plan_id=?", (plan_id,)).fetchone()
        if r: return dict(r)
        if plan_id in DEFAULT_PRICES:
            p = DEFAULT_PRICES[plan_id]
            return {"plan_id": plan_id, "game": p["game"], "label": p["label"], "regular": p["reg"], "reseller": p["res"]}
    return None

def db_set_price(plan_id, regular, reseller):
    with get_db() as db:
        r = db.execute("SELECT game, label FROM prices WHERE plan_id=?", (plan_id,)).fetchone()
        if r:
            db.execute("UPDATE prices SET regular=?, reseller=? WHERE plan_id=?", (regular, reseller, plan_id))
        elif plan_id in DEFAULT_PRICES:
            p = DEFAULT_PRICES[plan_id]
            db.execute("INSERT INTO prices (plan_id, game, label, regular, reseller) VALUES (?,?,?,?,?)",
                       (plan_id, p["game"], p["label"], regular, reseller))
    push_data_to_github_bg()

def db_record_order(user_id, game, plan_label, price, key_delivered):
    with get_db() as db:
        db.execute(
            "INSERT INTO order_history (user_id, game, plan_label, price, key_delivered) VALUES (?,?,?,?,?)",
            (user_id, game, plan_label, price, key_delivered)
        )
    push_data_to_github_bg()

def db_get_last_purchase(user_id):
    with get_db() as db:
        row = db.execute("SELECT game, plan_label FROM order_history WHERE user_id=? ORDER BY id DESC LIMIT 1", (user_id,)).fetchone()
        if row:
            return f"{row['game']} ({row['plan_label']})"
    return "No Purchases Yet"

def db_get_user_orders(user_id):
    with get_db() as db:
        return db.execute("SELECT game, plan_label, price, key_delivered, timestamp FROM order_history WHERE user_id=? ORDER BY id DESC LIMIT 10", (user_id,)).fetchall()

def get_price(user_id, plan_id):
    is_res = db_is_reseller(user_id)
    plan = db_get_plan(plan_id)
    if plan:
        return plan["reseller"] if is_res else plan["regular"]
    return 0# (Paste Part 1 above this)

def stock_text():
    lines = [
        "╔═══════════════════════════╗",
        "║  📦 <b>LIVE WAREHOUSE INVENTORY</b>  ║",
        "╚═══════════════════════════╝",
        "\n👑 <b>SHINIGAMI AUTO PLAY:</b>"
    ]
    for p in ["shini_1d", "shini_3d", "shini_7d", "shini_15d", "shini_30d"]:
        pl = db_get_plan(p)
        label = pl["label"] if pl else p
        lines.append(f"  🔥 <code>{label:8}</code> [<code>{p}</code>] ➜ <b>{db_count_keys(p)} Pcs</b>")

    lines.append("\n🍏 <b>LYNX AUTO PLAY (iOS):</b>")
    for p in ["lynx_ios_1d", "lynx_ios_3d", "lynx_ios_7d", "lynx_ios_15d", "lynx_ios_30d"]:
        pl = db_get_plan(p)
        label = pl["label"] if pl else p
        lines.append(f"  🍏 <code>{label:8}</code> [<code>{p}</code>] ➜ <b>{db_count_keys(p)} Pcs</b>")

    lines.append("\n🤖 <b>LYNX AUTO PLAY (Android):</b>")
    for p in ["lynx_and_1d", "lynx_and_3d", "lynx_and_7d", "lynx_and_15d", "lynx_and_30d"]:
        pl = db_get_plan(p)
        label = pl["label"] if pl else p
        lines.append(f"  🤖 <code>{label:8}</code> [<code>{p}</code>] ➜ <b>{db_count_keys(p)} Pcs</b>")

    lines.append("\n👿 <b>AIM-AI CARROM ENGINE:</b>")
    for p in ["aim_1d", "aim_3d", "aim_7d", "aim_15d", "aim_30d", "aim_90d"]:
        pl = db_get_plan(p)
        label = pl["label"] if pl else p
        lines.append(f"  🔥 <code>{label:8}</code> [<code>{p}</code>] ➜ <b>{db_count_keys(p)} Pcs</b>")

    lines.append("\n👑 <b>AIM CARROM KING INVENTORY:</b>")
    for p in ["acn_3d","acn_7d","acn_30d","acp_3d","acp_7d","acp_30d"]:
        pl = db_get_plan(p)
        label = pl["label"] if pl else p
        lines.append(f"  💎 <code>{label:8}</code> [<code>{p}</code>] ➜ <b>{db_count_keys(p)} Pcs</b>")

    lines.append("\n🔥 <b>KOS ENGINE KEYS:</b>")
    for p in ["b1","b7","b15","b30","c1","c7","c15","c30","f1","f7","f30"]:
        pl = db_get_plan(p)
        gname = f"{pl['game']} ({pl['label']})" if pl else p
        lines.append(f"  ⚡ <code>{gname}</code> [<code>{p}</code>] ➜ <b>{db_count_keys(p)} Pcs</b>")
    
    lines.append("\n⚡ <b>BITAIM HACK SLOTS:</b>")
    for p in ["bit7","bit30","bit90","bitlt"]:
        pl = db_get_plan(p)
        label = pl["label"] if pl else p
        lines.append(f"  🔮 <code>Bitaim {label:10}</code> [<code>{p}</code>] ➜ <b>{db_count_keys(p)} Pcs</b>")

    lines.append("\n🐍 <b>SNAKE ENGINE SLOTS:</b>")
    for p in ["snkc_3d","snkc_10d","snkc_30d","snk8_3d","snk8_10d","snk8_30d"]:
        pl = db_get_plan(p)
        gname = f"{pl['game']} ({pl['label']})" if pl else p
        lines.append(f"  🐍 <code>{gname}</code> [<code>{p}</code>] ➜ <b>{db_count_keys(p)} Pcs</b>")
        
    lines.append("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)

def price_list_text():
    lines = [
        "╔═══════════════════════════╗",
        "║  💎 <b>OFFICIAL VIP PRICE CATALOG</b> ║",
        "╚═══════════════════════════╝",
        "\n👑 <b>SHINIGAMI AUTO PLAY:</b>"
    ]
    for p in ["shini_1d", "shini_3d", "shini_7d", "shini_15d", "shini_30d"]:
        item = db_get_plan(p)
        if item:
            lines.append(f"  👑 <b>{item['label']:8}</b> <code>[{p}]</code> ➜ <code>₹{item['regular']}</code> <i>[VIP: ₹{item['reseller']}]</i>")

    lines.append("\n🍏 <b>LYNX AUTO PLAY (iOS):</b>")
    for p in ["lynx_ios_1d", "lynx_ios_3d", "lynx_ios_7d", "lynx_ios_15d", "lynx_ios_30d"]:
        item = db_get_plan(p)
        if item:
            lines.append(f"  🍏 <b>{item['label']:8}</b> <code>[{p}]</code> ➜ <code>₹{item['regular']}</code> <i>[VIP: ₹{item['reseller']}]</i>")

    lines.append("\n🤖 <b>LYNX AUTO PLAY (Android):</b>")
    for p in ["lynx_and_1d", "lynx_and_3d", "lynx_and_7d", "lynx_and_15d", "lynx_and_30d"]:
        item = db_get_plan(p)
        if item:
            lines.append(f"  🤖 <b>{item['label']:8}</b> <code>[{p}]</code> ➜ <code>₹{item['regular']}</code> <i>[VIP: ₹{item['reseller']}]</i>")

    lines.append("\n👿 <b>AIM-AI ENGINE (CARROM POOL):</b>")
    for p in ["aim_1d", "aim_3d", "aim_7d", "aim_15d", "aim_30d", "aim_90d"]:
        item = db_get_plan(p)
        if item:
            lines.append(f"  🔥 <b>{item['label']:8}</b> <code>[{p}]</code> ➜ <code>₹{item['regular']}</code> <i>[VIP: ₹{item['reseller']}]</i>")

    lines.append("\n👑 <b>AIM CARROM KING (Normal):</b>")
    for p in ["acn_3d","acn_7d","acn_30d"]:
        item = db_get_plan(p)
        if item:
            lines.append(f"  💎 <b>{item['label']}</b> <code>[{p}]</code> ➜ <code>₹{item['regular']}</code> <i>[VIP: ₹{item['reseller']}]</i>")
        
    lines.append("\n👑 <b>AIM CARROM KING (Premium Auto Queue):</b>")
    for p in ["acp_3d","acp_7d","acp_30d"]:
        item = db_get_plan(p)
        if item:
            lines.append(f"  ⚡ <b>{item['label']}</b> <code>[{p}]</code> ➜ <code>₹{item['regular']}</code> <i>[VIP: ₹{item['reseller']}]</i>")

    lines.append("\n🔥 <b>KOS ENGINE VIP KEYS:</b>")
    for p in ["b1","b7","b15","b30","c1","c7","c15","c30","f1","f7","f30"]:
        item = db_get_plan(p)
        if item:
            lines.append(f"  🔮 <b>{item['game']} {item['label']}</b> <code>[{p}]</code> ➜ <code>₹{item['regular']}</code> <i>[VIP: ₹{item['reseller']}]</i>")
    
    lines.append("\n⚡ <b>BITAIM PREMIUM HACK:</b>")
    for p in ["bit7","bit30","bit90","bitlt"]:
        item = db_get_plan(p)
        if item:
            lines.append(f"  🎯 <b>Bitaim {item['label']}</b> <code>[{p}]</code> ➜ <code>₹{item['regular']}</code> <i>[VIP: ₹{item['reseller']}]</i>")

    lines.append("\n🐍 <b>SNAKE ENGINE VIP:</b>")
    for p in ["snkc_3d","snkc_10d","snkc_30d","snk8_3d","snk8_10d","snk8_30d"]:
        item = db_get_plan(p)
        if item:
            lines.append(f"  🐍 <b>{item['game']} {item['label']}</b> <code>[{p}]</code> ➜ <code>₹{item['regular']}</code> <i>[VIP: ₹{item['reseller']}]</i>")
        
    lines.append("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)

pending_orders   = {}
payment_requests = {}
awaiting_gmail   = {}
order_locks      = set()
PAYMENT_TIMEOUT  = 300

def get_main_dashboard(uid, name):
    role = "👑 VIP Reseller [Elite]" if db_is_reseller(uid) else "👤 Verified Customer"
    bal  = db_get_balance(uid)
    last_buy = db_get_last_purchase(uid)

    inline_kbd = [
        [InlineKeyboardButton("👑 Shinigami Auto play 🔥", callback_data="shini_menu")],
        [InlineKeyboardButton("🔥 Lynx Engine Auto play 🔥", callback_data="lynx_menu")],
        [InlineKeyboardButton("👿 AIM-AI CARROM ENGINE 🔥", callback_data="aim_ai_menu")],
        [InlineKeyboardButton("👑 AIM CARROM KING", callback_data="aim_menu")],
        [InlineKeyboardButton("🔥 KOS Engine Keys", callback_data="kos_menu"), InlineKeyboardButton("⚡ Bitaim Hack", callback_data="bitaim_menu")],
        [InlineKeyboardButton("🐍 Snake Engine", callback_data="snk_menu")],
        [InlineKeyboardButton("🎁 Referral & Earn (₹1 Per Friend)", callback_data="referral_menu")],
        [InlineKeyboardButton("💳 Add Balance", callback_data="add_bal"), InlineKeyboardButton("📜 My Orders", callback_data="orders_hist")],
        [InlineKeyboardButton("📥 Download App", url="https://t.me/hgfileall")],
        [InlineKeyboardButton("👑 Apply For Reseller Panel", callback_data="become_reseller")]
    ]
    
    if uid in ADMINS or db_is_script_admin(uid):
        inline_kbd.insert(6, [InlineKeyboardButton("🛠️ Script Key Generator [Admin]", callback_data="script_key_menu")])

    msg = (
        "╔═══════════════════════════╗\n"
        "║  👑 <b>HAPPY GAMER VIP STORE</b> 👑  ║\n"
        "╚═══════════════════════════╝\n"
        "✨ <i>The Most Advanced Instant Key Automation System</i>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Client:</b> <code>{name}</code>\n"
        f"💰 <b>Wallet Balance:</b> <code>₹{bal}.00</code> 💳\n"
        f"🛡️ <b>Account Rank:</b> {role}\n"
        f"🎮 <b>Last Purchased:</b> <i>{last_buy}</i>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ <b>Fast Automatic Key Delivery Guaranteed</b>\n"
        "1️⃣ Click <b>💳 Add Balance</b> to top up via Official UPI\n"
        "2️⃣ Send payment screenshot for instant credit\n"
        "3️⃣ Select your desired <b>VIP Hack Engine</b> to receive instant key!"
    )
    return msg, InlineKeyboardMarkup(inline_kbd)

def get_reply_keyboard():
    return ReplyKeyboardMarkup([
        ["🔑 All Hack Key buy", "Check Balance 💰"],
        ["🎁 Referral & Earn 💰", "➕Add Balance 💰"],
        ["📦 Stock", "📞 Admin Help"]
    ], resize_keyboard=True)

def get_payment_caption():
    return (
        "╔═══════════════════════════════════════╗\n"
        "║   🛡️ <b>HAPPY GAMER OFFICIAL PAYMENT</b> 🛡️   ║\n"
        "╚═══════════════════════════════════════╝\n\n"
        "📌 <b>Official Verified UPI ID:</b>\n"
        "👉 <code>sagarhalder22@axl</code> <i>(Tap to Copy)</i>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📸 <b>Send Payment Screenshot after payment.</b>\n"
        "⏳ <b>Verification Time:</b> 5 Minutes\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ <i>Balance will be credited directly to your wallet!</i>"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    name = update.effective_user.first_name
    username = update.effective_user.username or ""

    if db_is_banned(uid):
        await update.message.reply_text("🚫 <b>YOUR ACCOUNT IS BANNED!</b>", parse_mode="HTML")
        return

    referrer_id = 0
    if context.args and len(context.args) > 0:
        param = context.args[0]
        if param.startswith("ref_"):
            try:
                referrer_id = int(param.replace("ref_", ""))
            except Exception: pass

    ref_giver = db_register_user(uid, name, username, referrer_id)
    
    if ref_giver:
        try:
            await context.bot.send_message(
                chat_id=ref_giver,
                text=(
                    "🎉 <b>CONGRATULATIONS! REFERRAL BONUS CREDITED!</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 <b>New Joined User:</b> {name} (@{username})\n"
                    "💰 <b>Earned Reward:</b> +<code>₹1.00</code> credited to your wallet! 💳"
                ),
                parse_mode="HTML"
            )
        except Exception: pass

    msg, inline_markup = get_main_dashboard(uid, name)
    await update.message.reply_text(msg, parse_mode="HTML", reply_markup=get_reply_keyboard())
    await update.message.reply_text("👇 <b>Select your VIP Hack to Proceed:</b>", parse_mode="HTML", reply_markup=inline_markup)

async def handle_direct_payment(update: Update, context: ContextTypes.DEFAULT_TYPE, is_photo=False):
    user_id  = update.effective_user.id
    name     = update.effective_user.first_name
    username = update.effective_user.username or ""
    role_lbl = "👑 Reseller" if db_is_reseller(user_id) else "👤 Customer"

    task = asyncio.create_task(expire_payment(user_id, context))
    payment_requests[user_id] = {"task": task}

    amounts = [50, 70, 100, 140, 160, 200, 230, 240, 250, 320, 360, 430, 460, 560, 650, 730, 820, 1000, 1200, 1370, 1700, 2200]
    row, kbd = [], []
    for amt in amounts:
        row.append(InlineKeyboardButton(f"₹{amt}", callback_data=f"pay_{user_id}_{amt}"))
        if len(row) == 3: kbd.append(row); row = []
    if row: kbd.append(row)
    kbd.append([InlineKeyboardButton("❌ Reject Payment", callback_data=f"pay_{user_id}_reject")])

    if is_photo:
        photo_id = update.message.photo[-1].file_id
        await update.message.reply_text("✅ <b>Payment screenshot received!</b>\n⏳ Admin is verifying and crediting your balance within 5 minutes...", parse_mode="HTML")
        for admin_id in ADMINS:
            try:
                await context.bot.send_photo(
                    chat_id=admin_id, photo=photo_id,
                    caption=(
                        "🔔 <b>NEW PAYMENT SCREENSHOT RECEIVED</b>\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"👤 <b>User:</b> {name} (@{username})\n"
                        f"🆔 <b>ID:</b> <code>{user_id}</code> | {role_lbl}\n"
                        f"💰 Current Balance: <code>₹{db_get_balance(user_id)}</code>\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        "👇 <b>Select approved amount to credit:</b>"
                    ),
                    reply_markup=InlineKeyboardMarkup(kbd),
                    parse_mode="HTML"
                )
            except Exception: pass
    else:
        if os.path.exists(QR_PATH):
            with open(QR_PATH, "rb") as f:
                await update.message.reply_photo(photo=f, caption=get_payment_caption(), parse_mode="HTML")
        else:
            await update.message.reply_text(get_payment_caption(), parse_mode="HTML")

async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_direct_payment(update, context, is_photo=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    user_id = update.effective_user.id
    name = update.effective_user.first_name

    # Script Key Device ID generation input handler
    if context.user_data.get("script_gen_days"):
        days = context.user_data.pop("script_gen_days")
        device_id = text
        is_main = (user_id in ADMINS)
        
        if not is_main:
            price = SCRIPT_PRICES.get(days)
            if price is None:
                await update.message.reply_text("❌ <b>Invalid Days Selected!</b>", parse_mode="HTML")
                return
            s_bal = db_get_script_balance(user_id)
            if s_bal < price:
                await update.message.reply_text(f"❌ <b>INSUFFICIENT SCRIPT BALANCE!</b>\nRequired: ₹{price}\nYour Balance: ₹{s_bal}", parse_mode="HTML")
                return
            db_add_script_balance(user_id, -price)

        vip_key = generate_short_key(name, is_main)
        status_msg = await update.message.reply_text("⏳ <i>Connecting to Secure Cloud Server & Generating Key...</i>", parse_mode="HTML")
        success, expiry, err = append_to_gist(vip_key, device_id, days)
        
        if success:
            receipt_msg = (
                "╔═══════════════════════════╗\n"
                "║  👑 <b>SCRIPT KEY GENERATED!</b>   ║\n"
                "╚═══════════════════════════╝\n"
                f"👤 <b>Admin:</b> {name}\n"
                f"⏳ <b>Validity:</b> {days} Days (Expires: <code>{expiry}</code>)\n"
                f"📱 <b>Device ID:</b> <code>{device_id}</code>\n"
                "☁️ <b>Cloud Server:</b> <i>Key Activated ✅</i>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🔑 <b>YOUR VIP KEY:</b> <i>(👇 Tap to Copy)</i>\n\n"
                f"<code>{vip_key}</code>"
            )
            await status_msg.edit_text(receipt_msg, parse_mode="HTML")
        else:
            if not is_main:
                db_add_script_balance(user_id, price)
            await status_msg.edit_text(f"❌ <b>Cloud Update Failed:</b> <code>{err}</code>", parse_mode="HTML")
        return

    if user_id in awaiting_gmail:
        del awaiting_gmail[user_id]
        await update.message.reply_text(
            f"✅ <b>Reseller Application Submitted!</b>\nAdmin will review your email (<code>{text}</code>) shortly.",
            parse_mode="HTML"
        )
        for admin_id in ADMINS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"👑 <b>NEW RESELLER APPLICATION</b>\nUser: {name} (<code>{user_id}</code>)\nEmail: <code>{text}</code>",
                    parse_mode="HTML"
                )
            except Exception: pass
        return

    if text in ["🔑 All Hack Key buy", "/buy", "Buy Key 🔑"]:
        msg, inline_markup = get_main_dashboard(user_id, name)
        await update.message.reply_text("👇 <b>Select your VIP Hack to Proceed:</b>", parse_mode="HTML", reply_markup=inline_markup)
    elif text in ["Check Balance 💰", "/balance", "Balance 💰"]:
        bal = db_get_balance(user_id)
        is_res = "👑 VIP Reseller" if db_is_reseller(user_id) else "👤 Regular Customer"
        kbd = [
            [InlineKeyboardButton("➕ Add Balance", callback_data="add_bal")],
            [InlineKeyboardButton("📜 Order History", callback_data="orders_hist")]
        ]
        await update.message.reply_text(
            f"╔═══════════════════════════╗\n"
            f"║    💰 <b>YOUR WALLET BALANCE</b>    ║\n"
            f"╚═══════════════════════════╝\n\n"
            f"👤 <b>Account:</b> {name}\n"
            f"💵 <b>Current Balance:</b> <code>₹{bal}.00</code> 💳\n"
            f"🎖️ <b>Account Rank:</b> {is_res}\n\n"
            f"⚡ <i>Instant deduction on automated key purchases!</i>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(kbd)
        )
    elif text in ["➕Add Balance 💰", "Add Balance 💳", "/addbal"]:
        await handle_direct_payment(update, context, is_photo=False)
    elif text in ["📦 Stock", "/stock"]:
        await update.message.reply_text(stock_text(), parse_mode="HTML")
    elif text in ["📞 Admin Help", "Admin Help 📞", "/help"]:
        await update.message.reply_text(
            f"╔═══════════════════════════╗\n"
            f"║      📞 <b>CUSTOMER SUPPORT</b>     ║\n"
            f"╚═══════════════════════════╝\n\n"
            f"For instant VIP assistance, inquiries, or custom reseller quotas:\n\n"
            f"👉 <b>Official Admin:</b> {ADMIN_USERNAME}\n"
            f"⚡ Active Time: 10:00 AM - 12:00 AM IST",
            parse_mode="HTML"
        )
    elif text in ["🎁 Referral & Earn 💰", "/referral", "/ref"]:
        await send_referral_panel(update, context, user_id)
    else:
        msg, inline_markup = get_main_dashboard(user_id, name)
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=get_reply_keyboard())

async def send_referral_panel(update_or_query, context, user_id):
    bot_info = await context.bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"
    ref_count = db_get_referral_count(user_id)
    earned_total = ref_count * 1
    
    text = (
        "╔═══════════════════════════╗\n"
        "║  🎁 <b>REFERRAL & EARN SYSTEM</b>  ║\n"
        "╚═══════════════════════════╝\n\n"
        "Share your referral link with friends or groups!\n"
        "💰 <b>Earn ₹1.00 directly to your wallet</b> for every person who joins using your link!\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 <b>Your Total Referrals:</b> <code>{ref_count} Friends</code>\n"
        f"💵 <b>Total Cash Earned:</b> <code>₹{earned_total}.00</code> 💳\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔗 <b>Your Exclusive Referral Link:</b>\n"
        f"👉 <code>{ref_link}</code> <i>(Tap to Copy)</i>"
    )
    
    keyboard = [
        [InlineKeyboardButton("📤 Share Link", url=f"https://t.me/share/url?url={ref_link}&text=Join%20Happy%20Gamer%20VIP%20Store%20for%20Instant%20Hack%20Keys!")],
        [InlineKeyboardButton("◀️ Back to Main Menu", callback_data="back_main")]
    ]
    
    if hasattr(update_or_query, "message") and update_or_query.message:
        await update_or_query.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update_or_query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    name = query.from_user.first_name

    if query.data == "back_main":
        msg, inline_markup = get_main_dashboard(user_id, name)
        await query.edit_message_text(msg, parse_mode="HTML", reply_markup=inline_markup)
        return

    if query.data == "add_bal":
        if os.path.exists(QR_PATH):
            with open(QR_PATH, "rb") as f:
                await query.message.reply_photo(photo=f, caption=get_payment_caption(), parse_mode="HTML")
        else:
            await query.message.reply_text(get_payment_caption(), parse_mode="HTML")
        return

    if query.data == "referral_menu":
        await send_referral_panel(query, context, user_id)
        return

    # --- SCRIPT KEY MENU ---
    if query.data == "script_key_menu":
        if user_id not in ADMINS and not db_is_script_admin(user_id):
            await query.answer("Access Denied", show_alert=True)
            return
        
        is_main = (user_id in ADMINS)
        bal_text = "UNLIMITED [Main Admin]" if is_main else f"₹{db_get_script_balance(user_id)}.00"
        
        kbd = [
            [InlineKeyboardButton(f"⚡ 1 Day (₹{SCRIPT_PRICES[1]})", callback_data="sgen_1"), InlineKeyboardButton(f"⚡ 3 Days (₹{SCRIPT_PRICES[3]})", callback_data="sgen_3")],
            [InlineKeyboardButton(f"🔥 7 Days (₹{SCRIPT_PRICES[7]})", callback_data="sgen_7"), InlineKeyboardButton(f"⚡ 15 Days (₹{SCRIPT_PRICES[15]})", callback_data="sgen_15")],
            [InlineKeyboardButton(f"👑 30 Days (₹{SCRIPT_PRICES[30]})", callback_data="sgen_30"), InlineKeyboardButton(f"⚡ 90 Days (₹{SCRIPT_PRICES[90]})", callback_data="sgen_90")],
            [InlineKeyboardButton("◀️ Back to Main", callback_data="back_main")]
        ]
        await query.edit_message_text(
            "╔═══════════════════════════╗\n"
            "║  🛠️ <b>SCRIPT KEY GENERATOR</b>   ║\n"
            "╚═══════════════════════════╝\n\n"
            f"💰 <b>Your Script Balance:</b> <code>{bal_text}</code>\n\n"
            "Select validity duration for the Script VIP Key:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(kbd)
        )
        return

    if query.data.startswith("sgen_"):
        if user_id not in ADMINS and not db_is_script_admin(user_id): return
        days = int(query.data.replace("sgen_", ""))
        context.user_data["script_gen_days"] = days
        await query.edit_message_text(
            "╔═══════════════════════════╗\n"
            "║   📱 <b>DEVICE ID REQUIRED</b>     ║\n"
            "╚═══════════════════════════╝\n\n"
            f"Validity: <b>{days} Days</b>\n\n"
            "👉 Please type & send the <b>Target Device ID</b> in chat:",
            parse_mode="HTML"
        )
        return

    # --- SHINIGAMI AUTO PLAY MENU ---
    if query.data == "shini_menu":
        p1 = get_price(user_id, "shini_1d"); p3 = get_price(user_id, "shini_3d")
        p7 = get_price(user_id, "shini_7d"); p15 = get_price(user_id, "shini_15d")
        p30 = get_price(user_id, "shini_30d")

        keyboard = [
            [InlineKeyboardButton(f"⚡ 1 Day (₹{p1})", callback_data="buy_shini_1d"), InlineKeyboardButton(f"⚡ 3 Days (₹{p3})", callback_data="buy_shini_3d")],
            [InlineKeyboardButton(f"🔥 7 Days (₹{p7})", callback_data="buy_shini_7d"), InlineKeyboardButton(f"⚡ 15 Days (₹{p15})", callback_data="buy_shini_15d")],
            [InlineKeyboardButton(f"👑 30 Days (₹{p30})", callback_data="buy_shini_30d")],
            [InlineKeyboardButton("◀️ Back to Main Menu", callback_data="back_main")]
        ]
        text = (
            "╔═══════════════════════════╗\n"
            "║  👑 <b>SHINIGAMI AUTO PLAY</b> 🔥 ║\n"
            "╚═══════════════════════════╝\n"
            "📋 <b>Price List:</b>\n"
            f"• 1 Days — <code>₹{p1}</code>\n"
            f"• 3 Days — <code>₹{p3}</code>\n"
            f"• 7 Days — <code>₹{p7}</code>\n"
            f"• 15 Days — <code>₹{p15}</code>\n"
            f"• 30 Days — <code>₹{p30}</code>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ <i>Instant Auto Key • 100% Safe</i>"
        )
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # --- LYNX ENGINE AUTO PLAY MENU ---
    if query.data == "lynx_menu":
        keyboard = [
            [InlineKeyboardButton("🍏 Lynx Cheats iOS", callback_data="lynx_ios_sub")],
            [InlineKeyboardButton("🤖 Lynx Cheats Android", callback_data="lynx_and_sub")],
            [InlineKeyboardButton("◀️ Back to Main Menu", callback_data="back_main")]
        ]
        text = (
            "╔═══════════════════════════╗\n"
            "║  🔥 <b>LYNX ENGINE AUTO PLAY</b> 🔥 ║\n"
            "╚═══════════════════════════╝\n\n"
            "Select your platform (iOS or Android):"
        )
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "lynx_ios_sub":
        p1 = get_price(user_id, "lynx_ios_1d"); p3 = get_price(user_id, "lynx_ios_3d")
        p7 = get_price(user_id, "lynx_ios_7d"); p15 = get_price(user_id, "lynx_ios_15d")
        p30 = get_price(user_id, "lynx_ios_30d")
        keyboard = [
            [InlineKeyboardButton(f"🍏 1D (₹{p1})", callback_data="buy_lynx_ios_1d"), InlineKeyboardButton(f"🍏 3D (₹{p3})", callback_data="buy_lynx_ios_3d")],
            [InlineKeyboardButton(f"🍏 7D (₹{p7})", callback_data="buy_lynx_ios_7d"), InlineKeyboardButton(f"🍏 15D (₹{p15})", callback_data="buy_lynx_ios_15d")],
            [InlineKeyboardButton(f"🍏 30D (₹{p30})", callback_data="buy_lynx_ios_30d")],
            [InlineKeyboardButton("◀️ Back", callback_data="lynx_menu")]
        ]
        text = (
            "🌟 <b>LYNX CHEATS IOS PRICE LIST</b> ✅\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🍏 1D PRICE 🔜 <code>₹{p1}</code> / $3.5\n"
            f"🍏 3D PRICE ✍️ <code>₹{p3}</code> / $6\n"
            f"🍏 7D PRICE ⌨ <code>₹{p7}</code> / $9\n"
            f"🍏 15D PRICE ⌨ <code>₹{p15}</code> / $15\n"
            f"🍏 30D PRICE ⌨ <code>₹{p30}</code> / $23\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ <i>Instant Auto Key • iOS Non-Jailbreak / Jailbreak</i>"
        )
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "lynx_and_sub":
        p1 = get_price(user_id, "lynx_and_1d"); p3 = get_price(user_id, "lynx_and_3d")
        p7 = get_price(user_id, "lynx_and_7d"); p15 = get_price(user_id, "lynx_and_15d")
        p30 = get_price(user_id, "lynx_and_30d")
        keyboard = [
            [InlineKeyboardButton(f"🤖 1D (₹{p1})", callback_data="buy_lynx_and_1d"), InlineKeyboardButton(f"🤖 3D (₹{p3})", callback_data="buy_lynx_and_3d")],
            [InlineKeyboardButton(f"🤖 7D (₹{p7})", callback_data="buy_lynx_and_7d"), InlineKeyboardButton(f"🤖 15D (₹{p15})", callback_data="buy_lynx_and_15d")],
            [InlineKeyboardButton(f"🤖 30D (₹{p30})", callback_data="buy_lynx_and_30d")],
            [InlineKeyboardButton("◀️ Back", callback_data="lynx_menu")]
        ]
        text = (
            "🌟 <b>LYNX CHEATS ANDROID PRICE LIST</b> ✅\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 1D PRICE ⌨ <code>₹{p1}</code> / $1.5\n"
            f"🤖 3D PRICE ⌨ <code>₹{p3}</code> / $3\n"
            f"🤖 7D PRICE ⌨ <code>₹{p7}</code> / $5\n"
            f"🤖 15D PRICE ⌨ <code>₹{p15}</code> / $9\n"
            f"🤖 30D PRICE ⌨ <code>₹{p30}</code> / $14\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ <i>Instant Auto Key • Root & No-Root Supported</i>"
        )
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # --- AIM-AI CARROM ENGINE MENU ---
    if query.data == "aim_ai_menu":
        p1 = get_price(user_id, "aim_1d"); p3 = get_price(user_id, "aim_3d")
        p7 = get_price(user_id, "aim_7d"); p15 = get_price(user_id, "aim_15d")
        p30 = get_price(user_id, "aim_30d"); p90 = get_price(user_id, "aim_90d")

        keyboard = [
            [InlineKeyboardButton(f"⚡ 01 Day (₹{p1})", callback_data="buy_aim_1d"), InlineKeyboardButton(f"⚡ 03 Days (₹{p3})", callback_data="buy_aim_3d")],
            [InlineKeyboardButton(f"🔥 07 Days (₹{p7})", callback_data="buy_aim_7d"), InlineKeyboardButton(f"⚡ 15 Days (₹{p15})", callback_data="buy_aim_15d")],
            [InlineKeyboardButton(f"👑 30 Days (₹{p30})", callback_data="buy_aim_30d"), InlineKeyboardButton(f"⚡ 90 Days (₹{p90})", callback_data="buy_aim_90d")],
            [InlineKeyboardButton("◀️ Back to Main Menu", callback_data="back_main")]
        ]
        text = (
            "╔═══════════════════════════╗\n"
            "║  👿 <b>AIM-AI ENGINE (CARROM)</b> 🔥 ║\n"
            "╚═══════════════════════════╝\n"
            "💎 <b>OFFICIAL CARROM PRICE CATALOG:</b>\n"
            f"• ⌛ 01 Day    ──── <code>₹{p1}</code>\n"
            f"• ⌛ 03 Days   ──── <code>₹{p3}</code>\n"
            f"• ⌛ 07 Days   ──── <code>₹{p7}</code> 🔥\n"
            f"• ⌛ 15 Days   ──── <code>₹{p15}</code>\n"
            f"• ⌛ 30 Days   ──── <code>₹{p30}</code> 👑\n"
            f"• ⌛ 90 Days   ──── <code>₹{p90}</code> ⚡\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔒 <i>100% Anti-Ban Safe Engine • Instant Auto Key</i>"
        )
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # --- AIM CARROM KING MENU ---
    if query.data == "aim_menu":
        keyboard = [
            [InlineKeyboardButton("🟢 AIM Normal Engine", callback_data="aim_normal")],
            [InlineKeyboardButton("🔥 AIM Premium (Auto Queue)", callback_data="aim_premium")],
            [InlineKeyboardButton("◀️ Back to Main", callback_data="back_main")]
        ]
        await query.edit_message_text(
            "╔═══════════════════════════╗\n"
            "║   👑 <b>AIM CARROM KING STORE</b>   ║\n"
            "╚═══════════════════════════╝\n\n"
            "Select your version to view pricing & slots:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if query.data == "aim_normal":
        p3 = get_price(user_id, "acn_3d"); p7 = get_price(user_id, "acn_7d"); p30 = get_price(user_id, "acn_30d")
        keyboard = [
            [InlineKeyboardButton(f"⚡ 3 Days (₹{p3})", callback_data="buy_acn_3d")],
            [InlineKeyboardButton(f"🔥 1 Week (₹{p7})", callback_data="buy_acn_7d")],
            [InlineKeyboardButton(f"👑 1 Month (₹{p30})", callback_data="buy_acn_30d")],
            [InlineKeyboardButton("◀️ Back", callback_data="aim_menu")]
        ]
        text = (
            "╔═══════════════════════════╗\n"
            "║   🟢 <b>AIM NORMAL CARROM</b>    ║\n"
            "╚═══════════════════════════╝\n"
            "💎 <b>Instant Pricing:</b>\n"
            f"• 3 Days ➜ <code>₹{p3}</code>\n"
            f"• 1 Week ➜ <code>₹{p7}</code>\n"
            f"• 1 Month ➜ <code>₹{p30}</code>"
        )
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "aim_premium":
        p3 = get_price(user_id, "acp_3d"); p7 = get_price(user_id, "acp_7d"); p30 = get_price(user_id, "acp_30d")
        keyboard = [
            [InlineKeyboardButton(f"⚡ 3 Days (₹{p3})", callback_data="buy_acp_3d")],
            [InlineKeyboardButton(f"🔥 1 Week (₹{p7})", callback_data="buy_acp_7d")],
            [InlineKeyboardButton(f"👑 1 Month (₹{p30})", callback_data="buy_acp_30d")],
            [InlineKeyboardButton("◀️ Back", callback_data="aim_menu")]
        ]
        text = (
            "╔═══════════════════════════╗\n"
            "║  ⚡ <b>AIM PREMIUM (AUTO QUEUE)</b> ║\n"
            "╚═══════════════════════════╝\n"
            "💎 <b>Instant Pricing:</b>\n"
            f"• 3 Days ➜ <code>₹{p3}</code>\n"
            f"• 1 Week ➜ <code>₹{p7}</code>\n"
            f"• 1 Month ➜ <code>₹{p30}</code>"
        )
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # --- KOS MENU ---
    if query.data == "kos_menu":
        keyboard = [
            [InlineKeyboardButton("🎱 8 Ball Pool Panel", callback_data="kos_8b")],
            [InlineKeyboardButton("🎯 Carrom Pool Panel", callback_data="kos_cp")],
            [InlineKeyboardButton("🔥 FreeFire Ultra Panel", callback_data="kos_ff")],
            [InlineKeyboardButton("◀️ Back to Main", callback_data="back_main")]
        ]
        await query.edit_message_text("Select target game:", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "kos_8b":
        p1 = get_price(user_id, "b1"); p7 = get_price(user_id, "b7"); p15 = get_price(user_id, "b15"); p30 = get_price(user_id, "b30")
        keyboard = [
            [InlineKeyboardButton(f"⚡ 1 Day (₹{p1})", callback_data="buy_b1"), InlineKeyboardButton(f"⚡ 7 Days (₹{p7})", callback_data="buy_b7")],
            [InlineKeyboardButton(f"⚡ 15 Days (₹{p15})", callback_data="buy_b15"), InlineKeyboardButton(f"⚡ 30 Days (₹{p30})", callback_data="buy_b30")],
            [InlineKeyboardButton("◀️ Back", callback_data="kos_menu")]
        ]
        await query.edit_message_text(f"🎱 <b>KOS 8 BALL POOL VIP</b>\n• 1 Day ➜ ₹{p1} | 7 Days ➜ ₹{p7} | 15 Days ➜ ₹{p15} | 30 Days ➜ ₹{p30}", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "kos_cp":
        p1 = get_price(user_id, "c1"); p7 = get_price(user_id, "c7"); p15 = get_price(user_id, "c15"); p30 = get_price(user_id, "c30")
        keyboard = [
            [InlineKeyboardButton(f"⚡ 1 Day (₹{p1})", callback_data="buy_c1"), InlineKeyboardButton(f"⚡ 7 Days (₹{p7})", callback_data="buy_c7")],
            [InlineKeyboardButton(f"⚡ 15 Days (₹{p15})", callback_data="buy_c15"), InlineKeyboardButton(f"⚡ 30 Days (₹{p30})", callback_data="buy_c30")],
            [InlineKeyboardButton("◀️ Back", callback_data="kos_menu")]
        ]
        await query.edit_message_text(f"🎯 <b>KOS CARROM POOL VIP</b>\n• 1 Day ➜ ₹{p1} | 7 Days ➜ ₹{p7} | 15 Days ➜ ₹{p15} | 30 Days ➜ ₹{p30}", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "kos_ff":
        p1 = get_price(user_id, "f1"); p7 = get_price(user_id, "f7"); p30 = get_price(user_id, "f30")
        keyboard = [
            [InlineKeyboardButton(f"⚡ 1 Day (₹{p1})", callback_data="buy_f1"), InlineKeyboardButton(f"⚡ 7 Days (₹{p7})", callback_data="buy_f7")],
            [InlineKeyboardButton(f"⚡ 30 Days (₹{p30})", callback_data="buy_f30")],
            [InlineKeyboardButton("◀️ Back", callback_data="kos_menu")]
        ]
        await query.edit_message_text(f"🔥 <b>KOS FREEFIRE PANEL VIP</b>\n• 1 Day ➜ ₹{p1} | 7 Days ➜ ₹{p7} | 30 Days ➜ ₹{p30}", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # BITAIM MENU
    if query.data == "bitaim_menu":
        p7 = get_price(user_id, "bit7"); p30 = get_price(user_id, "bit30")
        p90 = get_price(user_id, "bit90"); plt = get_price(user_id, "bitlt")
        keyboard = [
            [InlineKeyboardButton(f"⚡ 7 Days (₹{p7})", callback_data="buy_bit7"), InlineKeyboardButton(f"⚡ 30 Days (₹{p30})", callback_data="buy_bit30")],
            [InlineKeyboardButton(f"⚡ 90 Days (₹{p90})", callback_data="buy_bit90"), InlineKeyboardButton(f"👑 Lifetime (₹{plt})", callback_data="buy_bitlt")],
            [InlineKeyboardButton("◀️ Back", callback_data="back_main")]
        ]
        await query.edit_message_text(f"⚡ <b>BITAIM PREMIUM HACK</b>\n• 7 Days: ₹{p7} | 30 Days: ₹{p30}\n• 90 Days: ₹{p90} | Lifetime: ₹{plt}", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # SNAKE MENU
    if query.data == "snk_menu":
        keyboard = [
            [InlineKeyboardButton("🐍 Snake Carrom Pool", callback_data="snkc_sub")],
            [InlineKeyboardButton("🐍 Snake 8 Ball Pool", callback_data="snk8_sub")],
            [InlineKeyboardButton("◀️ Back", callback_data="back_main")]
        ]
        await query.edit_message_text("Select Snake Engine version:", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "snkc_sub":
        p3 = get_price(user_id, "snkc_3d"); p10 = get_price(user_id, "snkc_10d"); p30 = get_price(user_id, "snkc_30d")
        keyboard = [
            [InlineKeyboardButton(f"⚡ 3 Days (₹{p3})", callback_data="buy_snkc_3d"), InlineKeyboardButton(f"⚡ 10 Days (₹{p10})", callback_data="buy_snkc_10d")],
            [InlineKeyboardButton(f"⚡ 30 Days (₹{p30})", callback_data="buy_snkc_30d")],
            [InlineKeyboardButton("◀️ Back", callback_data="snk_menu")]
        ]
        await query.edit_message_text(f"🐍 <b>SNAKE CARROM POOL</b>\n• 3 Days ➜ ₹{p3} | 10 Days ➜ ₹{p10} | 30 Days ➜ ₹{p30}", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "snk8_sub":
        p3 = get_price(user_id, "snk8_3d"); p10 = get_price(user_id, "snk8_10d"); p30 = get_price(user_id, "snk8_30d")
        keyboard = [
            [InlineKeyboardButton(f"⚡ 3 Days (₹{p3})", callback_data="buy_snk8_3d"), InlineKeyboardButton(f"⚡ 10 Days (₹{p10})", callback_data="buy_snk8_10d")],
            [InlineKeyboardButton(f"⚡ 30 Days (₹{p30})", callback_data="buy_snk8_30d")],
            [InlineKeyboardButton("◀️ Back", callback_data="snk_menu")]
        ]
        await query.edit_message_text(f"🐍 <b>SNAKE 8 BALL POOL</b>\n• 3 Days ➜ ₹{p3} | 10 Days ➜ ₹{p10} | 30 Days ➜ ₹{p30}", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # --- BUYING & INSTANT CONFIRMATION (WITH ANTI-DOUBLE-CLICK LOCK) ---
    if query.data.startswith("buy_"):
        plan_id = query.data.replace("buy_", "")
        plan = db_get_plan(plan_id)
        if not plan:
            await query.answer("Invalid plan", show_alert=True)
            return
        price = get_price(user_id, plan_id)
        pending_orders[user_id] = plan_id
        keyboard = [
            [InlineKeyboardButton("⚡ Confirm & Deliver Key", callback_data="confirm_buy")],
            [InlineKeyboardButton("❌ Cancel Order", callback_data="back_main")]
        ]
        confirm_text = f"🛒 <b>Confirm Purchase</b>\n🎮 Item: {plan['game']} ({plan['label']})\n💰 Price: <code>₹{price}</code>"
        await query.edit_message_text(confirm_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "confirm_buy":
        if user_id in order_locks:
            await query.answer("⏳ Processing your request, please wait...", show_alert=False)
            return

        if user_id not in pending_orders:
            await query.answer("✅ Order already processed or invalid session!", show_alert=False)
            return

        order_locks.add(user_id)
        
        try:
            plan_id = pending_orders[user_id]
            plan = db_get_plan(plan_id)
            if not plan:
                pending_orders.pop(user_id, None)
                await query.edit_message_text("❌ <b>Invalid Product Plan!</b>", parse_mode="HTML")
                return

            price = get_price(user_id, plan_id)
            bal = db_get_balance(user_id)

            if bal < price:
                pending_orders.pop(user_id, None)
                kbd = [[InlineKeyboardButton("➕ Add Balance Now", callback_data="add_bal")]]
                await query.edit_message_text(
                    f"⚠️ <b>INSUFFICIENT BALANCE!</b>\n\n"
                    f"Required: <code>₹{price}</code>\n"
                    f"Your Balance: <code>₹{bal}</code>\n"
                    f"Needed: <code>₹{price - bal}</code>\n\n"
                    f"Please add funds to your wallet.",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(kbd)
                )
                return

            if db_count_keys(plan_id) <= 0:
                pending_orders.pop(user_id, None)
                await query.edit_message_text(
                    f"⚠️ <b>OUT OF STOCK!</b>\n\n"
                    f"<code>{plan['game']} ({plan['label']})</code> is currently out of stock.\n"
                    f"Please contact admin {ADMIN_USERNAME} for quick restock.",
                    parse_mode="HTML"
                )
                return

            # Execute transaction
            key = db_pop_key(plan_id)
            if not key:
                pending_orders.pop(user_id, None)
                await query.edit_message_text("⚠️ <b>Stock depleted just now! Please try again.</b>", parse_mode="HTML")
                return

            # Remove pending order immediately
            pending_orders.pop(user_id, None)
            
            # Deduct balance & record
            db_add_balance(user_id, -price)
            db_record_order(user_id, plan["game"], plan["label"], price, key)
            new_bal = db_get_balance(user_id)

            success_msg = (
                "╔═══════════════════════════╗\n"
                "║   🎉 <b>KEY DELIVERED INSTANTLY</b>   ║\n"
                "╚═══════════════════════════╝\n\n"
                f"🎮 <b>Product:</b> {plan['game']} ({plan['label']})\n"
                f"💵 <b>Paid:</b> <code>₹{price}.00</code>\n"
                f"💳 <b>Remaining Balance:</b> <code>₹{new_bal}.00</code>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🔑 <b>YOUR VIP ACTIVATION KEY:</b> <i>(👇 Tap to Copy)</i>\n\n"
                f"<code>{key}</code>\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "📥 <b>Download Mod App:</b> https://t.me/hgfileall\n"
                "❤️ <i>Thank you for choosing Happy Gamer Official!</i>"
            )
            
            back_kbd = [[InlineKeyboardButton("◀️ Return to Dashboard", callback_data="back_main")]]
            await query.edit_message_text(success_msg, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(back_kbd))

            for admin_id in ADMINS:
                try:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=(
                            f"🛒 <b>AUTOMATED SALE SUCCESSFUL!</b>\n"
                            f"👤 <b>Buyer:</b> {name} (<code>{user_id}</code>)\n"
                            f"🎮 <b>Item:</b> {plan['game']} ({plan['label']})\n"
                            f"💰 <b>Amount:</b> ₹{price}\n"
                            f"🔑 <b>Delivered Key:</b> <code>{key}</code>"
                        ),
                        parse_mode="HTML"
                    )
                except Exception: pass

        finally:
            order_locks.discard(user_id)
        return

    if query.data == "orders_hist":
        orders = db_get_user_orders(user_id)
        if not orders:
            await query.edit_message_text("📜 <b>You haven't made any purchases yet.</b>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="back_main")]]))
            return
        lines = [
            "╔═══════════════════════════╗",
            "║    📜 <b>YOUR RECENT PURCHASES</b>   ║",
            "╚═══════════════════════════╝\n"
        ]
        for o in orders:
            lines.append(f"• <b>{o['game']}</b> ({o['plan_label']}) - ₹{o['price']}\n  🔑 <code>{o['key_delivered']}</code>\n  📅 {o['timestamp']}\n")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        kbd = [[InlineKeyboardButton("◀️ Back to Main", callback_data="back_main")]]
        await query.edit_message_text("\n".join(lines), parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kbd))
        return

    if query.data == "become_reseller":
        is_res = db_is_reseller(user_id)
        if is_res:
            await query.edit_message_text(
                "👑 <b>YOU ARE ALREADY A VIP RESELLER!</b>\n\nYou enjoy special discounted reseller prices on all keys automatically.",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="back_main")]])
            )
            return
        awaiting_gmail[user_id] = True
        await query.edit_message_text(
            "╔═══════════════════════════╗\n"
            "║   👑 <b>APPLY FOR RESELLER PANEL</b>  ║\n"
            "╚═══════════════════════════╝\n\n"
            "VIP Resellers get wholesale discounted pricing on all keys.\n\n"
            "👉 Please <b>reply with your Email Address</b> to submit application:",
            parse_mode="HTML"
        )
        return

    # Admin Payment Approval Handler
    if query.data.startswith("pay_"):
        if user_id not in ADMINS:
            await query.answer("Admin only", show_alert=True)
            return
        parts = query.data.split("_")
        target_id = int(parts[1])
        action = parts[2]

        if action == "reject":
            req = payment_requests.pop(target_id, None)
            if req and req.get("task"): req["task"].cancel()
            try: await context.bot.send_message(target_id, "❌ <b>Your payment verification was rejected.</b>", parse_mode="HTML")
            except Exception: pass
            await query.edit_message_caption("❌ <b>Payment Rejected</b>", parse_mode="HTML")
            return
        amount = int(action)
        req = payment_requests.pop(target_id, None)
        if req and req.get("task"): req["task"].cancel()

        new_bal = db_add_balance(target_id, amount)
        try:
            await context.bot.send_message(
                target_id,
                f"🎉 <b>PAYMENT APPROVED!</b>\n💰 <b>₹{amount}</b> has been added to your wallet!\n💳 <b>Current Balance:</b> <code>₹{new_bal}.00</code>",
                parse_mode="HTML"
            )
        except Exception: pass
        await query.edit_message_caption(f"✅ <b>Approved ₹{amount} for User {target_id}</b>", parse_mode="HTML")
        return

async def expire_payment(user_id, context):
    await asyncio.sleep(PAYMENT_TIMEOUT)
    if user_id in payment_requests:
        del payment_requests[user_id]
        try: await context.bot.send_message(user_id, "⚠️ Payment verification session timed out. Please submit your receipt again.")
        except Exception: pass

# --- ALL ADMIN COMMANDS ---
async def cmd_resetdata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    init_db(force_fresh=True)
    push_data_to_github_bg()
    await update.message.reply_text("🧹 <b>DATABASE & BALANCES COMPLETELY PURGED!</b>\nAll user balances reset to <b>₹0.00</b> and synchronized with GitHub.", parse_mode="HTML")

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    help_text = (
        "╔═══════════════════════════════════════╗\n"
        "║   👑 <b>ADMIN FULL CONTROL & KEY CODES</b>   ║\n"
        "╚═══════════════════════════════════════╝\n\n"
        "🔑 <b>How to Add Stock Key (/addkey):</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "👑 <b>SHINIGAMI AUTO PLAY:</b>\n"
        "• <code>/addkey shini_1d YOUR_KEY</code> (1 Day)\n"
        "• <code>/addkey shini_3d YOUR_KEY</code> (3 Days)\n"
        "• <code>/addkey shini_7d YOUR_KEY</code> (7 Days)\n"
        "• <code>/addkey shini_15d YOUR_KEY</code> (15 Days)\n"
        "• <code>/addkey shini_30d YOUR_KEY</code> (30 Days)\n\n"
        "🍏 <b>LYNX AUTO PLAY (iOS):</b>\n"
        "• <code>/addkey lynx_ios_1d YOUR_KEY</code> (1 Day)\n"
        "• <code>/addkey lynx_ios_3d YOUR_KEY</code> (3 Days)\n"
        "• <code>/addkey lynx_ios_7d YOUR_KEY</code> (7 Days)\n"
        "• <code>/addkey lynx_ios_15d YOUR_KEY</code> (15 Days)\n"
        "• <code>/addkey lynx_ios_30d YOUR_KEY</code> (30 Days)\n\n"
        "🤖 <b>LYNX AUTO PLAY (Android):</b>\n"
        "• <code>/addkey lynx_and_1d YOUR_KEY</code> (1 Day)\n"
        "• <code>/addkey lynx_and_3d YOUR_KEY</code> (3 Days)\n"
        "• <code>/addkey lynx_and_7d YOUR_KEY</code> (7 Days)\n"
        "• <code>/addkey lynx_and_15d YOUR_KEY</code> (15 Days)\n"
        "• <code>/addkey lynx_and_30d YOUR_KEY</code> (30 Days)\n\n"
        "👿 <b>AIM-AI CARROM:</b>\n"
        "• <code>/addkey aim_1d YOUR_KEY</code> (01 Day)\n"
        "• <code>/addkey aim_3d YOUR_KEY</code> (03 Days)\n"
        "• <code>/addkey aim_7d YOUR_KEY</code> (07 Days)\n"
        "• <code>/addkey aim_15d YOUR_KEY</code> (15 Days)\n"
        "• <code>/addkey aim_30d YOUR_KEY</code> (30 Days)\n"
        "• <code>/addkey aim_90d YOUR_KEY</code> (90 Days)\n\n"
        "👑 <b>AIM CARROM KING (Normal & Premium):</b>\n"
        "• <code>/addkey acn_3d YOUR_KEY</code> (Normal 3 Days)\n"
        "• <code>/addkey acn_7d YOUR_KEY</code> (Normal 1 Week)\n"
        "• <code>/addkey acn_30d YOUR_KEY</code> (Normal 1 Month)\n"
        "• <code>/addkey acp_3d YOUR_KEY</code> (Premium 3 Days)\n"
        "• <code>/addkey acp_7d YOUR_KEY</code> (Premium 1 Week)\n"
        "• <code>/addkey acp_30d YOUR_KEY</code> (Premium 1 Month)\n\n"
        "🔥 <b>KOS ENGINE:</b>\n"
        "• <b>Carrom:</b> <code>/addkey c1 KEY</code> | <code>/addkey c7 KEY</code> | <code>/addkey c15 KEY</code> | <code>/addkey c30 KEY</code>\n"
        "• <b>8 Ball:</b> <code>/addkey b1 KEY</code> | <code>/addkey b7 KEY</code> | <code>/addkey b15 KEY</code> | <code>/addkey b30 KEY</code>\n"
        "• <b>FreeFire:</b> <code>/addkey f1 KEY</code> | <code>/addkey f7 KEY</code> | <code>/addkey f30 KEY</code>\n\n"
        "🐍 <b>SNAKE ENGINE:</b>\n"
        "• <b>Carrom:</b> <code>/addkey snkc_3d KEY</code> | <code>/addkey snkc_10d KEY</code> | <code>/addkey snkc_30d KEY</code>\n"
        "• <b>8 Ball:</b> <code>/addkey snk8_3d KEY</code> | <code>/addkey snk8_10d KEY</code> | <code>/addkey snk8_30d KEY</code>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🛠️ <b>Other Admin Commands:</b>\n"
        "• <code>/resetdata</code> / <code>/resetall</code> ➜ Reset all database balances to 0\n"
        "• <code>/scriptkey &lt;days&gt; &lt;device_id&gt;</code> ➜ Auto Script Key Generate\n"
        "• <code>/removescriptkey &lt;device_id&gt;</code> ➜ Remove & Deactivate Script Device Key\n"
        "• <code>/cleangist</code> ➜ Delete Expired Keys from Cloud\n"
        "• <code>/testgist</code> ➜ Test Cloud Connection\n"
        "• <code>/stock</code> ➜ Check Live Stock\n"
        "• <code>/prices</code> ➜ View All Price Catalog\n"
        "• <code>/add &lt;id&gt; &lt;amount&gt;</code> ➜ Add User Balance\n"
        "• <code>/broadcast &lt;text&gt;</code> ➜ Broadcast Message to All Users\n"
        "• <code>/ban &lt;id&gt;</code> / <code>/unban &lt;id&gt;</code> ➜ Ban or Unban User\n"
        "• <code>/reply &lt;id&gt; &lt;text&gt;</code> ➜ Direct Reply to User\n"
        "• <code>/deliver &lt;id&gt; &lt;key&gt;</code> ➜ Deliver Key Directly\n"
        "• <code>/setprice &lt;code&gt; &lt;reg&gt; &lt;res&gt;</code> ➜ Update Plan Price\n"
        "• <code>/addreseller &lt;id&gt;</code> / <code>/removereseller &lt;id&gt;</code> ➜ Reseller Control\n"
        "• <code>/addscriptadmin &lt;id&gt;</code> ➜ Add Script Key Admin\n"
        "• <code>/removescriptadmin &lt;id&gt;</code> ➜ Remove Script Key Admin\n"
        "• <code>/scriptadmins</code> ➜ View All Script Admins\n"
        "• <code>/addscriptbal &lt;id&gt; &lt;amount&gt;</code> ➜ Add Balance for Script Admins\n"
        "• <code>/resellers</code> ➜ View All Resellers"
    )
    await update.message.reply_text(help_text, parse_mode="HTML")

async def cmd_addscriptadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        uid = int(context.args[0])
        db_add_script_admin(uid)
        await update.message.reply_text(f"✅ User <code>{uid}</code> added as Script Key Generator Admin!", parse_mode="HTML")
    except Exception: await update.message.reply_text("Usage: <code>/addscriptadmin &lt;user_id&gt;</code>", parse_mode="HTML")

async def cmd_removescriptadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        uid = int(context.args[0])
        db_remove_script_admin(uid)
        await update.message.reply_text(f"🗑️ User <code>{uid}</code> removed from Script Key Admins.", parse_mode="HTML")
    except Exception: await update.message.reply_text("Usage: <code>/removescriptadmin &lt;user_id&gt;</code>", parse_mode="HTML")

async def cmd_scriptadmins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    admins = db_all_script_admins()
    if not admins:
        await update.message.reply_text("ℹ️ No custom Script Admins configured.", parse_mode="HTML")
        return
    msg = "🛠️ <b>ACTIVE SCRIPT KEY ADMINS:</b>\n\n"
    for a in admins:
        bal = db_get_script_balance(a)
        msg += f"• <code>{a}</code> | Script Balance: <b>₹{bal}</b>\n"
    await update.message.reply_text(msg, parse_mode="HTML")

async def cmd_addscriptbal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        uid = int(context.args[0])
        amt = int(context.args[1])
        new_bal = db_add_script_balance(uid, amt)
        await update.message.reply_text(f"✅ Added <b>₹{amt}</b> Script Balance to <code>{uid}</code>!\n💰 Current Script Balance: <b>₹{new_bal}</b>", parse_mode="HTML")
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=f"🎉 <b>SCRIPT BALANCE CREDITED!</b>\nAdmin added <b>₹{amt}</b> to your Script Balance.\n💰 Current Balance: <b>₹{new_bal}</b>",
                parse_mode="HTML"
            )
        except Exception: pass
    except Exception: await update.message.reply_text("Usage: <code>/addscriptbal &lt;user_id&gt; &lt;amount&gt;</code>", parse_mode="HTML")

async def cmd_scriptkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = update.effective_user.first_name
    is_main = (user_id in ADMINS)
    
    if not is_main and not db_is_script_admin(user_id):
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "💡 <b>Usage:</b> <code>/scriptkey &lt;days&gt; &lt;device_id&gt;</code>\n"
            "<b>Example:</b> <code>/scriptkey 30 550e8400e29b41d4a716446655440000</code>",
            parse_mode="HTML"
        )
        return

    try:
        days = int(context.args[0])
        device_id = context.args[1].strip()
        
        if not is_main:
            price = SCRIPT_PRICES.get(days)
            if price is None:
                await update.message.reply_text("❌ <b>Invalid Days!</b> Allowed: 1, 3, 7, 15, 30, 90", parse_mode="HTML")
                return
            s_bal = db_get_script_balance(user_id)
            if s_bal < price:
                await update.message.reply_text(f"❌ <b>INSUFFICIENT SCRIPT BALANCE!</b>\nRequired: ₹{price}\nYour Balance: ₹{s_bal}", parse_mode="HTML")
                return
            db_add_script_balance(user_id, -price)
            
        vip_key = generate_short_key(name, is_main)
        
        status_msg = await update.message.reply_text("⏳ <i>Connecting to Secure Cloud Server & Generating Key...</i>", parse_mode="HTML")
        success, expiry, err = append_to_gist(vip_key, device_id, days)
        
        if success:
            receipt_msg = (
                "╔═══════════════════════════╗\n"
                "║  👑 <b>SCRIPT KEY GENERATED!</b>   ║\n"
                "╚═══════════════════════════╝\n"
                f"👤 <b>Admin:</b> {name}\n"
                f"⏳ <b>Validity:</b> {days} Days (Expires: <code>{expiry}</code>)\n"
                f"📱 <b>Device ID:</b> <code>{device_id}</code>\n"
                "☁️ <b>Cloud Server:</b> <i>Key Activated ✅</i>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🔑 <b>YOUR VIP KEY:</b> <i>(👇 Tap to Copy)</i>\n\n"
                f"<code>{vip_key}</code>"
            )
            await status_msg.edit_text(receipt_msg, parse_mode="HTML")
        else:
            if not is_main:
                db_add_script_balance(user_id, price)
            await status_msg.edit_text(f"❌ <b>Cloud Update Failed:</b> <code>{err}</code>", parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ <b>Error:</b> <code>{e}</code>", parse_mode="HTML")

async def cmd_removescriptkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMINS and not db_is_script_admin(user_id):
        return
    if not context.args:
        await update.message.reply_text("💡 <b>Usage:</b> <code>/removescriptkey &lt;device_id&gt;</code>", parse_mode="HTML")
        return
    device_id = context.args[0].strip()
    status_msg = await update.message.reply_text("⏳ <i>Searching & removing key from Cloud Server...</i>", parse_mode="HTML")
    success, count, err = remove_device_from_gist(device_id)
    if success:
        await status_msg.edit_text(
            "╔═══════════════════════════╗\n"
            "║  🗑️ <b>SCRIPT KEY REMOVED!</b>    ║\n"
            "╚═══════════════════════════╝\n\n"
            f"📱 <b>Device ID:</b> <code>{device_id}</code>\n"
            f"⚡ <b>Removed Entries:</b> <code>{count}</code>\n"
            "☁️ <b>Cloud Status:</b> <i>Key has been deactivated & deleted from server!</i>",
            parse_mode="HTML"
        )
    else:
        await status_msg.edit_text(f"❌ <b>Removal Failed:</b> <code>{err}</code>", parse_mode="HTML")

async def cmd_cleangist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    purged = purge_expired_gist_keys()
    await update.message.reply_text(f"🧹 <b>Server Database Cleaned!</b>\nRemoved <code>{purged}</code> expired keys.", parse_mode="HTML")

async def cmd_testgist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    if not GITHUB_TOKEN:
        await update.message.reply_text("❌ Server Token is not configured.", parse_mode="HTML")
        return
    headers = get_auth_headers()
    res = requests.get(f"https://api.github.com/gists/{GIST_ID}", headers=headers, timeout=10)
    if res.status_code == 200:
        await update.message.reply_text("✅ <b>Secure API Connection Successful!</b>", parse_mode="HTML")
    else:
        await update.message.reply_text(f"❌ <b>Server Error ({res.status_code}):</b> {res.text}", parse_mode="HTML")

async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    if not context.args:
        await update.message.reply_text("💡 <b>Usage:</b> <code>/broadcast &lt;Text&gt;</code>", parse_mode="HTML")
        return
    msg = " ".join(context.args)
    users = db_get_all_users()
    for uid in users:
        if db_is_banned(uid): continue
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 <b>OFFICIAL ANNOUNCEMENT:</b>\n\n{msg}", parse_mode="HTML")
            await asyncio.sleep(0.05)
        except Exception: pass
    await update.message.reply_text(f"✅ Broadcast sent to {len(users)} users.", parse_mode="HTML")

async def cmd_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        uid = int(context.args[0])
        db_ban_user(uid)
        await update.message.reply_text(f"🚨 User {uid} banned.", parse_mode="HTML")
    except Exception: await update.message.reply_text("Usage: <code>/ban &lt;user_id&gt;</code>", parse_mode="HTML")

async def cmd_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        uid = int(context.args[0])
        db_unban_user(uid)
        await update.message.reply_text(f"✅ User {uid} unbanned.", parse_mode="HTML")
    except Exception: await update.message.reply_text("Usage: <code>/unban &lt;user_id&gt;</code>", parse_mode="HTML")

async def cmd_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        target_id = int(context.args[0])
        msg_text  = " ".join(context.args[1:])
        await context.bot.send_message(chat_id=target_id, text=f"📩 <b>Official Admin Message:</b>\n\n{msg_text}", parse_mode="HTML")
        await update.message.reply_text(f"✅ Message sent to <code>{target_id}</code>", parse_mode="HTML")
    except Exception: await update.message.reply_text("Usage: <code>/reply &lt;user_id&gt; &lt;message&gt;</code>", parse_mode="HTML")

async def cmd_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        uid = int(context.args[0]); amount = int(context.args[1])
        new_bal = db_add_balance(uid, amount)
        await update.message.reply_text(f"✅ Credited ₹{amount} to <code>{uid}</code>\n💳 New Balance: ₹{new_bal}", parse_mode="HTML")
        try: await context.bot.send_message(uid, f"🎉 <b>Admin added ₹{amount} to your wallet!</b>\n💳 Current Balance: ₹{new_bal}", parse_mode="HTML")
        except Exception: pass
    except Exception: await update.message.reply_text("Usage: <code>/add &lt;user_id&gt; &lt;amount&gt;</code>", parse_mode="HTML")

async def cmd_addkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        plan = context.args[0].lower(); key = context.args[1]
        db_add_key(plan, key)
        count = db_count_keys(plan)
        await update.message.reply_text(f"✅ Key added to <code>{plan}</code>!\n📦 Stock: {count} available.", parse_mode="HTML")
    except Exception: await update.message.reply_text("Usage: <code>/addkey &lt;plan_id&gt; &lt;key&gt;</code>", parse_mode="HTML")

async def cmd_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(stock_text(), parse_mode="HTML")

async def cmd_prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(price_list_text(), parse_mode="HTML")

async def cmd_deliver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        uid = int(context.args[0]); key = " ".join(context.args[1:])
        await context.bot.send_message(uid, f"🎁 <b>VIP KEY DELIVERED BY ADMIN:</b>\n\n<code>{key}</code>", parse_mode="HTML")
        await update.message.reply_text(f"✅ Delivered to <code>{uid}</code>", parse_mode="HTML")
    except Exception: await update.message.reply_text("Usage: <code>/deliver &lt;user_id&gt; &lt;key&gt;</code>", parse_mode="HTML")

async def cmd_setprice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        plan_id = context.args[0].lower(); reg = int(context.args[1]); res = int(context.args[2])
        db_set_price(plan_id, reg, res)
        await update.message.reply_text(f"✅ Price updated for <code>{plan_id}</code>\nRegular: ₹{reg} | Reseller: ₹{res}", parse_mode="HTML")
    except Exception: await update.message.reply_text("Usage: <code>/setprice &lt;plan_id&gt; &lt;reg_price&gt; &lt;reseller_price&gt;</code>", parse_mode="HTML")

async def cmd_addreseller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        uid = int(context.args[0])
        db_add_reseller(uid)
        await update.message.reply_text(f"👑 User <code>{uid}</code> added to Resellers!", parse_mode="HTML")
        try: await context.bot.send_message(uid, "👑 <b>CONGRATULATIONS! You have been granted VIP Reseller status!</b>\nYou now get discounted prices across the store.", parse_mode="HTML")
        except Exception: pass
    except Exception: await update.message.reply_text("Usage: <code>/addreseller &lt;user_id&gt;</code>", parse_mode="HTML")

async def cmd_removereseller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    try:
        uid = int(context.args[0])
        db_remove_reseller(uid)
        await update.message.reply_text(f"User <code>{uid}</code> removed from Resellers.", parse_mode="HTML")
    except Exception: await update.message.reply_text("Usage: <code>/removereseller &lt;user_id&gt;</code>", parse_mode="HTML")

async def cmd_resellers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    resellers = db_all_resellers()
    if not resellers:
        await update.message.reply_text("No VIP Resellers found.", parse_mode="HTML")
        return
    msg = "👑 <b>ACTIVE VIP RESELLERS:</b>\n" + "\n".join([f"• <code>{uid}</code>" for uid in resellers])
    await update.message.reply_text(msg, parse_mode="HTML")

# --- MAIN RUNNER ---
if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is missing!")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start",          start))
    app.add_handler(CommandHandler("help",           cmd_help))
    app.add_handler(CommandHandler("resetdata",      cmd_resetdata))
    app.add_handler(CommandHandler("resetall",       cmd_resetdata))
    app.add_handler(CommandHandler("cleardb",        cmd_resetdata))
    app.add_handler(CommandHandler("referral",       send_referral_panel))
    app.add_handler(CommandHandler("ref",            send_referral_panel))
    app.add_handler(CommandHandler("broadcast",      cmd_broadcast))
    app.add_handler(CommandHandler("sendall",        cmd_broadcast))
    app.add_handler(CommandHandler("scriptkey",      cmd_scriptkey))
    app.add_handler(CommandHandler("removescriptkey", cmd_removescriptkey))
    app.add_handler(CommandHandler("delscriptkey",    cmd_removescriptkey))
    app.add_handler(CommandHandler("scriptremove",    cmd_removescriptkey))
    app.add_handler(CommandHandler("cleangist",      cmd_cleangist))
    app.add_handler(CommandHandler("testgist",       cmd_testgist))
    app.add_handler(CommandHandler("ban",            cmd_ban))
    app.add_handler(CommandHandler("unban",          cmd_unban))
    app.add_handler(CommandHandler("reply",          cmd_reply))
    app.add_handler(CommandHandler("add",            cmd_add))
    app.add_handler(CommandHandler("addkey",         cmd_addkey))
    app.add_handler(CommandHandler("stock",          cmd_stock))
    app.add_handler(CommandHandler("prices",         cmd_prices))
    app.add_handler(CommandHandler("deliver",        cmd_deliver))
    app.add_handler(CommandHandler("setprice",       cmd_setprice))
    app.add_handler(CommandHandler("addreseller",    cmd_addreseller))
    app.add_handler(CommandHandler("removereseller", cmd_removereseller))
    app.add_handler(CommandHandler("resellers",      cmd_resellers))
    
    # SCRIPT ADMIN COMMANDS
    app.add_handler(CommandHandler("addscriptadmin", cmd_addscriptadmin))
    app.add_handler(CommandHandler("removescriptadmin", cmd_removescriptadmin))
    app.add_handler(CommandHandler("scriptadmins",   cmd_scriptadmins))
    app.add_handler(CommandHandler("addscriptbal",   cmd_addscriptbal))
    
    app.add_handler(MessageHandler(filters.PHOTO,    receive_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot is starting...")
    app.run_polling()
